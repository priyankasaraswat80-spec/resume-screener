import matplotlib
matplotlib.use('Agg')   # for deployment (no GUI issues)

from flask import Flask, render_template, request
import os
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt

app = Flask(__name__)

# 🔹 Skill list
skills_list = [
    "python", "java", "c++", "sql", "machine learning",
    "data analysis", "excel", "communication", "teamwork",
    "deep learning", "nlp", "flask", "html", "css",
    "recruitment", "hr", "management", "teaching", "education"
]

# 🔹 Predefined Job Descriptions
job_data = {
    "IT": "Looking for a Python Developer with machine learning, SQL, Flask, HTML, CSS and problem solving skills.",
    "HR": "Looking for HR professional with recruitment, communication, teamwork, management and hiring experience.",
    "EDUCATION": "Looking for teacher with teaching, education, classroom management and communication skills."
}

# 🔹 Read PDF
def read_pdf(file):
    text = ""
    try:
        reader = PdfReader(file)
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()
    except:
        pass
    return text

# 🔹 Extract skills
def extract_skills(text):
    text = text.lower()
    return [skill for skill in skills_list if skill in text]

# 🔹 ML Score
def ml_score(resume_text, job_desc):
    texts = [resume_text, job_desc]
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(texts)
    similarity = cosine_similarity(vectors[0], vectors[1])[0][0]
    return round(similarity * 100, 2)

# 🔹 Detect Role
def detect_role(text):
    text = text.lower()
    if "python" in text or "developer" in text:
        return "IT"
    elif "recruitment" in text or "hr" in text:
        return "HR"
    elif "teaching" in text or "education" in text:
        return "EDUCATION"
    return "General"

# 🔹 Ranking
def rank_resumes(job_desc, role):
    folder = f"resumes/{role}"
    results = []

    if not os.path.exists(folder):
        return []

    for file in os.listdir(folder):
        if file.endswith(".pdf"):
            path = os.path.join(folder, file)
            resume_text = read_pdf(path)
            score = ml_score(resume_text, job_desc)
            results.append((file, score))

    results.sort(key=lambda x: x[1], reverse=True)
    return results[:5]

# 🔹 Chart
def create_chart(rankings):
    if not rankings:
        return None

    os.makedirs("static", exist_ok=True)

    names = [x[0] for x in rankings]
    scores = [x[1] for x in rankings]

    plt.figure(figsize=(6,4))
    plt.bar(names, scores)
    plt.xticks(rotation=30)
    plt.ylabel("Score (%)")
    plt.title("Top Resume Ranking")

    chart_path = "static/chart.png"
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    return chart_path

# 🔹 Home
@app.route('/')
def home():
    return render_template('index.html')

# 🔹 Upload (FIXED)
@app.route('/upload', methods=['GET', 'POST'])
def upload():

    if request.method == 'GET':
        return render_template('index.html')

    files = request.files.getlist('resume')
    user_input = request.form['job_desc'].upper()

    if not files or files[0].filename == "":
        return render_template('index.html', result="No file uploaded")

    # Select job description
    if user_input in job_data:
        job_desc = job_data[user_input]
    else:
        job_desc = user_input

    resume_text = read_pdf(files[0])

    if not resume_text.strip():
        return render_template('index.html', result="Resume is empty")

    role = detect_role(job_desc)
    score = ml_score(resume_text, job_desc)

    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_desc)

    common_skills = list(set(resume_skills).intersection(job_skills))
    missing = list(set(job_skills) - set(resume_skills))

    rankings = rank_resumes(job_desc, role)
    chart = create_chart(rankings)

    return render_template(
        'index.html',
        result=f"Your Resume Score: {score}%",
        skills=f"Matched Skills: {common_skills}",
        rankings=rankings,
        chart=chart,
        role=role,
        score=score,
        missing=missing
    )

# 🔹 Run
if __name__ == '__main__':
    app.run()