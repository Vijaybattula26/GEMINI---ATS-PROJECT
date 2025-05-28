
Markdown

# Intelligent Candidate Evaluation ATS

## Table of Contents
1.  [Project Overview](#project-overview)
2.  [Features](#features)
3.  [Technologies Used](#technologies-used)
4.  [Setup & Installation](#setup--installation)
    * [Prerequisites](#prerequisites)
    * [Cloning the Repository](#cloning-the-repository)
    * [Setting up a Virtual Environment](#setting-up-a-virtual-environment)
    * [Installing Dependencies](#installing-dependencies)
    * [Google Gemini API Key Configuration](#google-gemini-api-key-configuration)
    * [Running the Application](#running-the-application)
5.  [Usage](#usage)
6.  [Project Structure](#project-structure)
7.  [Database](#database)
8.  [Future Enhancements](#future-enhancements)
9.  [License](#license)
10. [Acknowledgments](#acknowledgments)

---

## 1. Project Overview

The Intelligent Candidate Evaluation ATS (Applicant Tracking System) is a web-based tool designed to streamline the resume screening process. Leveraging Google's Gemini-1.5-Flash Generative AI model, it automates the parsing of candidate resumes, extracts key information, and evaluates their fit against specific job descriptions. This helps recruiters and hiring managers quickly identify the most suitable candidates, saving time and improving hiring efficiency.

## 2. Features

* **Resume Upload:** Supports PDF and DOCX file formats for resume uploads.
* **Text Extraction:** Extracts comprehensive text content from uploaded resumes.
* **AI-Powered Resume Parsing:** Utilizes Google Gemini-1.5-Flash to parse raw resume text into structured data (name, email, phone, education, experience, skills, summary).
* **Job Description Evaluation:** Allows users to input a job description for AI-driven candidate matching.
* **Match Scoring:** Generates a numerical match score (out of 100) indicating candidate suitability.
* **Detailed Evaluation Summary:** Provides a qualitative summary from Gemini, highlighting strengths, gaps, and reasons for the match score.
* **Candidate Listing:** Displays a list of processed candidates with their basic info and match scores.
* **Detailed Candidate View:** Offers a modal view to see all parsed data and the full job match summary for a specific candidate.
* **Persistent Data Storage:** Uses SQLite to store resume content, parsed data, scores, and evaluation summaries.
* **Responsive Web Interface:** Built with Flask and Bootstrap 5 for a modern and user-friendly experience.

## 3. Technologies Used

* **Backend:**
    * **Python 3.x**
    * **Flask:** Web framework for building the API and serving HTML.
    * **Google Generative AI SDK (`google-generativeai`):** For interacting with the Gemini API.
    * **`pypdf`:** For extracting text from PDF documents.
    * **`docx2txt`:** For extracting text from DOCX documents.
    * **`python-dotenv`:** For managing environment variables (API keys).
    * **`sqlite3`:** Built-in Python library for database operations.
* **Frontend:**
    * **HTML5**
    * **CSS3**
    * **JavaScript (ES6+)**
    * **Bootstrap 5.3.3:** For responsive design and UI components.

## 4. Setup & Installation

Follow these steps to get the project up and running on your local machine.

### Prerequisites

* **Python 3.8+** (recommended)
* **`pip`** (Python package installer, usually comes with Python)
* **Git** (for cloning the repository)
* A **Google Cloud Project** with the **Gemini API enabled** and an **API Key**.

### Cloning the Repository

First, clone the repository to your local machine:

```bash
git clone <repository_url> # Replace <repository_url> with your actual repo URL
cd Intelligent-Candidate-Evaluation-ATS # Or whatever your project folder is named
Setting up a Virtual Environment
It's highly recommended to use a virtual environment to manage project dependencies.

Bash

python -m venv venv
Activate the virtual environment:

Windows:
Bash

.\venv\Scripts\activate
macOS/Linux:
Bash

source venv/bin/activate
(Your terminal prompt should now show (venv) indicating the virtual environment is active.)

Installing Dependencies
Once your virtual environment is active, install the required Python packages:

Bash

pip install -r requirements.txt
If you don't have a requirements.txt yet, create one in your project root with the following content:

requirements.txt content:

Flask
python-dotenv
google-generativeai
pypdf
docx2txt
Then run: pip install -r requirements.txt

Google Gemini API Key Configuration
Obtain a Gemini API Key:

Go to the Google AI Studio.
Create a new API Key if you don't have one.
Ensure the gemini-1.5-flash model is available and enabled for your project.
Create a .env file:
In the root directory of your project (the same directory as app.py), create a file named .env (note the leading dot).

Add your API Key to .env:
Open the .env file and add the following line, replacing YOUR_GOOGLE_API_KEY with your actual API key:

GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY
Important: Do not commit your .env file to public repositories (e.g., GitHub). Add .env to your .gitignore file.

Running the Application
After all dependencies are installed and the API key is configured, you can run the Flask application:

Bash

python app.py
You will see output indicating that the Flask development server is running, usually at http://127.0.0.1:5000/.

5. Usage
Open your browser: Navigate to http://127.0.0.1:5000/.
Upload Resume: In the "Upload Resume" section, click "Select file" and choose a candidate's resume (PDF or DOCX). Click "Upload Resume".
Provide Job Description: In the "Provide Job Description & Process" section, paste the full job description for the role you are hiring for.
Process Candidate: Click the "Process Candidate" button. The application will send the resume and job description to Gemini for parsing and evaluation.
View Results:
A success/error message will appear at the top.
The "Candidates" list will update with the newly processed candidate, showing their name, filename, and match score.
Click "View Details" next to any candidate to open a modal with comprehensive parsed information (education, experience, skills, etc.) and the detailed job match summary from Gemini.
6. Project Structure
Intelligent-Candidate-Evaluation-ATS/
├── app.py                  # Main Flask application file
├── requirements.txt        # List of Python dependencies
├── .env                    # Environment variables (e.g., Google API Key) - **DO NOT COMMIT**
├── templates/
│   └── index.html          # Frontend HTML file with Bootstrap and JavaScript
├── uploads/                # Directory to store uploaded resumes (created automatically)
└── ats.db                  # SQLite database file (created automatically)
├── .gitignore              # Specifies intentionally untracked files to ignore
└── README.md               # This documentation file
7. Database
The application uses an SQLite database named ats.db. This database is automatically created upon the first run of app.py if it doesn't already exist. It stores:

id: Unique identifier for each resume.
filename: Original name of the uploaded resume file.
text_content: The raw extracted text from the resume.
parsed_data: JSON string of structured data extracted by Gemini.
score: Numerical match score.
job_match_summary: Full evaluation summary from Gemini.
8. Future Enhancements
User Authentication: Implement login/signup for secure access.
Multiple Job Descriptions: Allow saving and selecting from multiple job descriptions.
Advanced Filtering/Sorting: Add options to filter candidates by skills, experience, or sort by different criteria.
Resume Download: Provide an option to download the original uploaded resume or a generated report.
Dashboard Analytics: Display charts and graphs for overall candidate pool analysis.
External Database: Migrate from SQLite to a more robust database like PostgreSQL or MySQL for production.
Dockerization: Containerize the application for easier deployment.
UI/UX Improvements: Enhance the visual design and user experience.
Asynchronous Processing: Implement background tasks for long-running AI operations to improve responsiveness.
9. License
This project is licensed under the MIT License - see the LICENSE file for details (You might need to create a LICENSE file in your root directory if you want to explicitly state the MIT license).

10. Acknowledgments
Google Gemini API Documentation
Flask Documentation
Bootstrap 5 Documentation
The open-source community for various libraries and tools.
