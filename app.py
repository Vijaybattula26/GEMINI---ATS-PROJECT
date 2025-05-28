import os
import json # Ensure this is imported at the top
import re   # Ensure this is imported for regex
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import google.generativeai as genai # Back to Gemini
import pypdf
import docx2txt
import sqlite3

# Load environment variables from .env file (e.g., GOOGLE_API_KEY)
load_dotenv()

app = Flask(__name__)

# --- Configuration ---
# Folder to store uploaded resumes
app.config['UPLOAD_FOLDER'] = 'uploads'
# Ensure the uploads folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configure Google Gemini Pro API
# The API key is loaded from the .env file
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# Initialize the Generative Model with the correct model ID
model = genai.GenerativeModel('gemini-1.5-flash') # Changed from 'gemini-pro' based on your list_models output

# --- Database Setup (SQLite for simplicity) ---
DATABASE = 'ats.db'

def init_db():
    """Initializes the SQLite database and creates the 'resumes' table if it doesn't exist."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                text_content TEXT NOT NULL,
                parsed_data TEXT, -- JSON string of parsed data from Gemini
                score REAL,        -- Numerical match score
                job_match_summary TEXT -- Full evaluation summary from Gemini
            )
        ''')
        conn.commit()

# Initialize the database when the application starts
init_db()

# --- Helper Functions for Resume Text Extraction ---

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = pypdf.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or "" # Use .extract_text() and handle None
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}")
    return text

def extract_text_from_docx(docx_path):
    """Extracts text from a DOCX file."""
    text = ""
    try:
        text = docx2txt.process(docx_path)
    except Exception as e:
        print(f"Error extracting text from DOCX {docx_path}: {e}")
    return text

# --- Gemini Pro Interaction Functions ---

def parse_resume_with_gemini(resume_text):
    """
    Sends raw resume text to Gemini Pro for structured data extraction.
    Asks Gemini to return data in a specific JSON format.
    Handles potential markdown wrapping of JSON using regex for robustness.
    Returns a Python dictionary, or None if parsing fails.
    """
    prompt = f"""
    Analyze the following resume text and extract the following information in a JSON format.
    If a field is not found, use "N/A" for strings, empty array for lists, or appropriate default.
    Make sure the JSON is well-formed and directly parsable.

    Resume Text:
    {resume_text}

    Expected JSON format:
    {{
        "name": "string",
        "email": "string",
        "phone": "string",
        "linkedin": "string",
        "education": [
            {{"degree": "string", "major": "string", "university": "string", "years": "string"}}
        ],
        "experience": [
            {{"title": "string", "company": "string", "years": "string", "description": "string"}}
        ],
        "skills": ["skill1", "skill2", ...],
        "summary": "string"
    }}
    """
    try:
        response = model.generate_content(prompt)
        json_str = response.candidates[0].content.parts[0].text

        # --- MORE ROBUST JSON EXTRACTION USING REGEX ---
        # This regex looks for the content specifically inside ```json ... ``` blocks
        # re.DOTALL makes '.' match newlines, so it can capture multiline JSON
        match = re.search(r'```json\s*(.*?)\s*```', json_str, re.DOTALL)
        if match:
            cleaned_json_str = match.group(1).strip() # Extract content and strip whitespace
        else:
            # Fallback: if no markdown block is found, assume the entire string is JSON.
            # This is less common for Gemini, but a safeguard.
            cleaned_json_str = json_str.strip()

        # Debug print: See what's actually being fed to json.loads()
        print(f"DEBUG: Cleaned JSON string before loads():\n{cleaned_json_str[:500]}...") # Print first 500 chars

        # Parse the cleaned JSON string into a Python dictionary
        parsed_data = json.loads(cleaned_json_str)
        return parsed_data # Return the dictionary
    except Exception as e:
        print(f"Error calling Gemini for parsing: {e}")
        # Print raw response for debugging if parsing failed unexpectedly
        if 'response' in locals() and hasattr(response, 'candidates') and response.candidates:
            print(f"Raw Gemini response that caused error: {response.candidates[0].content.parts[0].text}")
        return None

def evaluate_candidate_with_gemini(job_description, resume_summary, skills):
    """
    Sends job description and extracted candidate info to Gemini Pro for evaluation.
    Asks Gemini to provide a score and a detailed match summary.
    """
    prompt = f"""
    Job Description:
    {job_description}

    Candidate Summary (from resume):
    {resume_summary}

    Candidate Skills:
    {', '.join(skills) if skills else 'None'}

    Based on the Job Description and Candidate information, provide:
    1. A match score out of 100 (e.g., "Score: 85/100").
    2. A brief summary of why this candidate is a good fit.
    3. Key strengths directly relevant to the job.
    4. Key gaps or areas where the candidate might not fully meet the requirements.

    Format your response clearly, starting with the score line.
    """
    try:
        response = model.generate_content(prompt)
        return response.candidates[0].content.parts[0].text
    except Exception as e:
        print(f"Error calling Gemini for evaluation: {e}")
        return "Evaluation failed: Could not get a response from Gemini."

# --- Flask Routes ---

@app.route('/')
def index():
    """Renders the main HTML page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_resume():
    """
    Handles resume file uploads, saves them, and extracts raw text content.
    Stores filename and raw text in the database.
    """
    if 'resume' not in request.files:
        return jsonify({'error': 'No file part in the request.'}), 400

    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No selected file.'}), 400

    if file:
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        text_content = ""
        if filename.lower().endswith('.pdf'):
            text_content = extract_text_from_pdf(filepath)
        elif filename.lower().endswith('.docx'):
            text_content = extract_text_from_docx(filepath)
        else:
            os.remove(filepath) # Clean up unsupported file
            return jsonify({'error': 'Unsupported file type. Please upload PDF or DOCX.'}), 400

        if not text_content.strip(): # Check if extracted text is empty or just whitespace
            os.remove(filepath) # Clean up file if text extraction failed
            return jsonify({'error': 'Could not extract readable text from the resume. Please check the file content.'}), 500

        # Store raw content in DB
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO resumes (filename, text_content) VALUES (?, ?)",
                (filename, text_content)
            )
            conn.commit()
            resume_id = cursor.lastrowid # Get the ID of the newly inserted resume

        return jsonify({
            'message': 'Resume uploaded and text extracted successfully!',
            'resume_id': resume_id,
            'filename': filename
        }), 200

@app.route('/process_resume/<int:resume_id>', methods=['POST'])
def process_resume(resume_id):
    """
    Processes a stored resume using Gemini Pro for parsing and evaluation against a job description.
    Updates the database with parsed data, score, and evaluation summary.
    """
    job_description = request.json.get('job_description', '').strip()
    if not job_description:
        return jsonify({'error': 'Job description is required for processing.'}), 400

    # Retrieve raw resume text from DB
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT text_content FROM resumes WHERE id = ?", (resume_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({'error': 'Resume not found in database.'}), 404
        resume_text = result[0]

    # --- Step 1: Parse Resume with Gemini Pro ---
    # parse_resume_with_gemini now returns a dictionary directly, or None
    parsed_data = parse_resume_with_gemini(resume_text)
    if parsed_data is None: # Check if a dictionary was successfully returned (not None)
        # The error message now reflects that the issue is within parse_resume_with_gemini
        return jsonify({'error': 'Failed to parse resume with Gemini. Check API key, model availability, or response format.'}), 500

    # Extract summary and skills for the next evaluation step
    resume_summary = parsed_data.get('summary', 'N/A')
    resume_skills = parsed_data.get('skills', [])

    # --- Step 2: Evaluate Candidate with Gemini Pro ---
    evaluation_result = evaluate_candidate_with_gemini(job_description, resume_summary, resume_skills)

    # Attempt to extract score (e.g., "Score: 85/100") using regex
    score_match = re.search(r'Score:\s*(\d+)/100', evaluation_result, re.IGNORECASE)
    score = float(score_match.group(1)) if score_match else 0.0 # Default to 0.0 if no score found

    # Update database with parsed data, score, and full evaluation summary
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE resumes SET parsed_data = ?, score = ?, job_match_summary = ? WHERE id = ?",
            (json.dumps(parsed_data), score, evaluation_result, resume_id)
        )
        conn.commit()

    return jsonify({
        'message': 'Resume processed and evaluated successfully!',
        'resume_id': resume_id,
        'parsed_data': parsed_data,
        'evaluation': evaluation_result,
        'score': score
    }), 200

@app.route('/candidates', methods=['GET'])
def get_candidates():
    """Fetches all processed candidates from the database, ordered by score."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # Select relevant fields for the candidate list display
        cursor.execute("SELECT id, filename, parsed_data, score, job_match_summary FROM resumes ORDER BY score DESC")
        candidates_raw = cursor.fetchall()

        candidates = []
        for candidate_id, filename, parsed_data_json, score, job_match_summary in candidates_raw:
            parsed_data = json.loads(parsed_data_json) if parsed_data_json else {}
            candidates.append({
                'id': candidate_id,
                'filename': filename,
                'name': parsed_data.get('name', 'N/A'),
                'email': parsed_data.get('email', 'N/A'),
                'score': score,
                'job_match_summary': job_match_summary # Include summary for quick list view if desired
            })
    return jsonify(candidates), 200

@app.route('/candidate_details/<int:resume_id>', methods=['GET'])
def get_candidate_details(resume_id):
    """Fetches detailed information for a specific candidate."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT filename, parsed_data, score, job_match_summary FROM resumes WHERE id = ?", (resume_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({'error': 'Candidate not found.'}), 404

        filename, parsed_data_json, score, job_match_summary = result
        parsed_data = json.loads(parsed_data_json) if parsed_data_json else {}

        return jsonify({
            'id': resume_id,
            'filename': filename,
            'parsed_data': parsed_data,
            'score': score,
            'job_match_summary': job_match_summary
        }), 200

# --- Main Application Runner ---
if __name__ == '__main__':
    # When running directly, start the Flask development server.
    # debug=True enables auto-reloading on code changes and provides a debugger.
    app.run(debug=True)