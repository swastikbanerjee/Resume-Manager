# from flask import Flask, render_template, request, jsonify
# import json

# app = Flask(__name__)
# with open('resume.json') as f:
#     resume_data = json.load(f)
# @app.route('/')
# def resume_form():
#     return render_template('resume_form.html', data=resume_data)
# @app.route('/submit', methods=['POST'])
# def submit_form():
#     submitted_data = request.form.to_dict()
#     print(submitted_data)
#     return jsonify({"message": "Form submitted successfully!"})
# if __name__ == '__main__':
#     app.run(debug=True)

import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
import fitz
from docx import Document
import google.generativeai as genai
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['GENERATED_JSON'] = 'resume.json'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def read_document(file_path):
    if file_path.endswith('.pdf'):
        try:
            pdf_document = fitz.open(file_path)
            text = ""
            for page_num in range(pdf_document.page_count):
                page = pdf_document.load_page(page_num)
                text += page.get_text() + "\n"
            pdf_document.close()
            return text
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return None
    elif file_path.endswith('.docx'):
        try:
            document = Document(file_path)
            text = "\n".join([para.text for para in document.paragraphs])
            return text
        except Exception as e:
            print(f"Error reading Word document: {e}")
            return None
    else:
        print("Unsupported file format")
        return None
@app.route('/')
def upload_page():
    return render_template('upload.html')
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        document_text = read_document(file_path)
        genai.configure(api_key='AIzaSyAy3EjjG0puD1quoYtmxkXPRQuz4RvtsPY')
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(f"""
        You are a professional resume parsing agent.
        So do as follows:
        1. Extract Personal Information of the applicant with keys being:
        a. Extract name of the applicant.
        b. Extract email of the applicant.
        c. Extract phone number of the applicant.
        d. Exract address of the applicant.
        e. Extract linkedin url of the applicant.
        2. Extract me the Summary of the applicant if mentioned.
        3. Extract me Work Experience details with keys being:
        a. Company name
        b. Mode of work (Offline/Online/Hybrid)
        c. Job Role
        d. Job Type (Full Time or Intern)
        e. Start Date
        f. End Date.
        4. Extract me Project details with keys being:
        a. Name of Project with short introduction of it, if mentioned
        b. Description of project.
        c. Start Date if any.
        d. End Date if any
        5. Extract me Achievement details with keys being:
        a. Heading with short introduction of it, if mentioned
        b. Description of the heading.
        c. Start Date if any.
        d. End Date if any:
        6. Extract me Education details with keys being:
        a. Degree/Course
        b. Field of Study (note: usually written alongside degree, extract from 'degree' key if that is the case)
        c. Institute
        d. Marks/Percentage/GPA
        e. Start Date if any
        f. End Date/ Passing Year
        7. Extract me Certification details with keys being:
        a. Certification Title
        b. Issuing Organization
        c. Date Of Issue
        8. List me all the skills from the following document.
        9. List me all the extracurricular activities/hobbies from the following document.
        10. List me all the language competencies from the following document.
        Resume of applicant: {document_text}
        You are to generate a valid JSON script as output. Properly deal with trailing commas while formatting the output file.
        Take this empty json format and fill it up:
        {{
            "Personal_Information": {{
                "Name": "",
                "Email": "",
                "Phone_Number": "",
                "Address": "",
                "LinkedIn_URL": ""
            }},
            "Summary": "",
            "Work_Experience": [
                {{
                    "Company_Name": "",
                    "Mode_of_Work": "",
                    "Job_Role": "",
                    "Job_Type": "",
                    "Start_Date": "",
                    "End_Date": "",
                }}
            ],
            "Projects": [
                {{
                    "Name_of_Project": "",
                    "Description": "",
                    "Start_Date": "",
                    "End_Date": ""
                }}
            ],
            "Achievements": [
                {{
                    "Heading": "",
                    "Description": "",
                    "Start_Date": "",
                    "End_Date": ""
                }}
            ],
            "Education": [
                {{
                    "Degree/Course": "",
                    "Field_of_Study": "",
                    "Institute": "",
                    "Marks/Percentage/GPA": "",
                    "Start_Date": "",
                    "End_Date": ""
                }}
            ],
            "Certifications": [
                {{
                    "Certification_Title": "",
                    "Issuing_Organization": "",
                    "Date_Of_Issue": ""
                }}
            ],
            "Skills": [],
            "Extracurricular_Activities": [],
            "Language_Competencies": [
                {{
                    "Language": "",
                    "Proficiency": ""
                }}
            ]
        }}""")
        lines = response.text.split('\n')
        truncated_lines = lines[1:-1]
        truncated_text = '\n'.join(truncated_lines)
        response_json = json.loads(truncated_text)
        output_filename = app.config['GENERATED_JSON']
        with open(output_filename, 'w') as json_file:
            json.dump(response_json, json_file, indent=4)
        return redirect(url_for('loading_page'))
@app.route('/loading')
def loading_page():
    return render_template('loading.html')
@app.route('/resume_form')
def resume_form():
    with open(app.config['GENERATED_JSON']) as f:
        resume_data = json.load(f)
    return render_template('resume_form.html', data=resume_data)
if __name__ == '__main__':
    app.run(debug=True)

