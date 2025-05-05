from flask import Flask, render_template, request, send_file
import spacy
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")

def extract_keywords(text):
    doc = nlp(text)
    return list(set([token.text.lower() for token in doc if token.pos_ in ["NOUN", "PROPN", "ADJ"] and len(token.text) > 2]))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/keywords', methods=['POST'])
def keywords():
    jd = request.form['job_description']
    keywords = extract_keywords(jd)
    return render_template('keywords.html', keywords=keywords)

@app.route('/generate', methods=['POST'])
def generate():
    jd = request.form['job_description']
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    linkedin = request.form['linkedin']
    github = request.form['github']
    address = request.form['address']
    summary = request.form['summary']
    skills = request.form['skills']
    experience = request.form['experience']
    education = request.form['education']
    certifications = request.form['certifications']
    projects = request.form['projects']  # New field

    jd_keywords = extract_keywords(jd)
    enriched_summary = summary + " Keywords: " + ", ".join(jd_keywords[:5])
    enriched_skills = skills + ", " + ", ".join(jd_keywords[:5])

    env = Environment(loader=FileSystemLoader('resume_templates'))
    template = env.get_template('resume_template.html')
    html_out = template.render(
        name=name, email=email, phone=phone,
        linkedin=linkedin, github=github, address=address,
        summary=enriched_summary, skills=enriched_skills,
        experience=experience, education=education,
        certifications=certifications, projects=projects
    )

    output_path = f'static/resume_{name.replace(" ", "_")}.pdf'
    with open(output_path, "w+b") as result_file:
        pisa_status = pisa.CreatePDF(html_out, dest=result_file)
        if pisa_status.err:
            return "Error generating PDF"

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
