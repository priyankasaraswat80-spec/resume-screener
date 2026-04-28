from flask import Flask, render_template, request
import re
import os

app = Flask(__name__)

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z ]', '', text)
    return text


@app.route("/", methods=["GET", "POST"])
def index():
    score = None

    if request.method == "POST":
        resume = request.form["resume"]
        job = request.form["job"]

        resume = clean_text(resume)
        job = clean_text(job)

        resume_words = set(resume.split())
        job_words = set(job.split())

        
        match = resume_words.intersection(job_words)

        if len(job_words) != 0:
            score = int((len(match) / len(job_words)) * 100)
        else:
            score = 0

    return render_template("index.html", score=score)



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
