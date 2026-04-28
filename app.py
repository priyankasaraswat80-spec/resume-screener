from flask import Flask, render_template, request
import re

app = Flask(__name__)

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z ]', '', text)
    return text


@app.route('/', methods=['GET', 'POST'])
def index():
    score = None

    if request.method == 'POST':
        resume = request.form['resume']
        job = request.form['job']

        resume = clean_text(resume)
        job = clean_text(job)

        resume_words = set(resume.split())
        job_words = set(job.split())

        match = len(resume_words & job_words)
        score = round((match / (len(job_words)+1)) * 100, 2)

    return render_template('index.html', score=score)

# 🔹 Run app
if __name__ == '__main__':
    app.run(debug=True)
