import os
import yaml
import json
import pdfplumber
from datetime import datetime

try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    GPT_ENABLED = True
except ImportError:
    print("OpenAI not available. GPT disabled.")
    GPT_ENABLED = False

# Load config
with open("config.yaml") as f:
    config = yaml.safe_load(f)

# Read your resume text
with pdfplumber.open("resume.pdf") as pdf:
    resume_text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

# Load GPT prompt template
if GPT_ENABLED:
    with open("prompts/cover_letter.txt") as f:
        prompt_template = f.read()

# Create log files
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
log_filename = f"applied_{timestamp}.txt"
skipped_log_filename = f"skipped_manual_{timestamp}.txt"

# Load previously applied jobs
APPLIED_JOBS_FILE = "applied_jobs.json"
if os.path.exists(APPLIED_JOBS_FILE):
    with open(APPLIED_JOBS_FILE, "r") as f:
        applied_jobs = set(json.load(f))
else:
    applied_jobs = set()

# Dummy job fetcher (replace with real scraping)
def fetch_jobs():
    return [
        {
            "title": "Python Developer",
            "company": "Acme Corp",
            "location": "New York, NY",
            "salary": "$120,000",
            "description": "We are hiring Python developers to work on web backends.",
            "url": "https://example.com/job1"
        },
        {
            "title": "DevOps Engineer",
            "company": "bottomline",
            "location": "Remote",
            "salary": "Not disclosed",
            "description": "Join our cloud infra team...",
            "url": "https://example.com/job2"
        },
        {
            "title": "SDE II",
            "company": "FreshTech",
            "location": "Remote",
            "salary": "",
            "description": "Looking for SDE II with 3+ years of experience.",
            "url": "https://example.com/job3"
        }
    ]

def generate_cover_letter(job):
    if not GPT_ENABLED:
        return "[GPT DISABLED: Cover letter could not be generated.]"
    try:
        prompt = prompt_template.replace("[JOB_DESCRIPTION]", job["description"]).replace("[YOUR_NAME]", "Your Name")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[Error generating cover letter: {str(e)}]"

def should_apply(job):
    title = job["title"].lower()
    company = job["company"].lower()
    if any(word.lower() in company for word in config["exclude_companies"]):
        return False
    if job["url"] in applied_jobs:
        print(f"Skipping already applied job: {job['title']} at {job['company']}")
        return False
    return any(k.lower() in title for k in config["job_keywords"])

def apply_to_job(job):
    print(f"Applying to: {job['title']} at {job['company']}")
    cover_letter = generate_cover_letter(job)

    # Write to log file
    with open(log_filename, "a") as log:
        log.write("="*50 + "\n")
        log.write(f"Job Title: {job['title']}\n")
        log.write(f"Company: {job['company']}\n")
        log.write(f"Location: {job.get('location', 'N/A')}\n")
        log.write(f"Salary: {job.get('salary', 'N/A')}\n")
        log.write(f"URL: {job['url']}\n\n")
        log.write("Generated Cover Letter:\n")
        log.write(cover_letter + "\n")
        log.write("="*50 + "\n\n")

    # Add to applied list and save
    applied_jobs.add(job["url"])
    with open(APPLIED_JOBS_FILE, "w") as f:
        json.dump(list(applied_jobs), f, indent=2)

def log_skipped_job(job, reason="Could not auto-apply"):
    with open(skipped_log_filename, "a") as log:
        log.write("="*50 + "\n")
        log.write(f"[SKIPPED - {reason}]\n")
        log.write(f"Job Title: {job['title']}\n")
        log.write(f"Company: {job['company']}\n")
        log.write(f"Location: {job.get('location', 'N/A')}\n")
        log.write(f"Salary: {job.get('salary', 'N/A')}\n")
        log.write(f"URL: {job['url']}\n")
        log.write(f"Description: {job['description']}\n")
        log.write("="*50 + "\n\n")

def main():
    jobs = fetch_jobs()
    for job in jobs:
        if should_apply(job):
            try:
                apply_to_job(job)
            except Exception as e:
                print(f"[!] Failed to auto-apply: {job['title']} at {job['company']}. Logging for manual.")
                log_skipped_job(job, reason=str(e))

if __name__ == "__main__":
    main()
