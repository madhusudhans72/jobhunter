## main.py
import os
import requests
import yaml
import openai
import pdfplumber
from bs4 import BeautifulSoup

# Load config
with open("config.yaml") as f:
    config = yaml.safe_load(f)

openai.api_key = os.getenv("OPENAI_API_KEY")

# Placeholder function for job scraping (replace with real logic)
def fetch_jobs():
    return [
        {"title": "Python Developer", "company": "Acme Corp", "description": "We need a Python dev...", "url": "https://example.com/job1"},
        {"title": "DevOps Engineer", "company": "bottomline", "description": "Cloud and infra role", "url": "https://example.com/job2"}
    ]

# Read your resume text
with pdfplumber.open("resume.pdf") as pdf:
    resume_text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

# Load GPT prompt
with open("prompts/cover_letter.txt") as f:
    prompt_template = f.read()

def generate_cover_letter(job):
    prompt = prompt_template.replace("[JOB_DESCRIPTION]", job["description"]).replace("[YOUR_NAME]", "Your Name")
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def should_apply(job):
    title = job["title"].lower()
    company = job["company"].lower()
    if any(word in company for word in config["exclude_companies"]):
        return False
    return any(k.lower() in title for k in config["job_keywords"])

def apply_to_job(job):
    print(f"Applying to: {job['title']} at {job['company']}")
    # cover_letter = generate_cover_letter(job)
    # Placeholder: Replace with API form submission or email logic
    # print("Generated Cover Letter:\n", cover_letter[:500], "...\n")

def main():
    jobs = fetch_jobs()
    for job in jobs:
        if should_apply(job):
            apply_to_job(job)

if __name__ == "__main__":
    main()

