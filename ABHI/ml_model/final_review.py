import csv
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
import joblib
import pandas as pd
from feature_extraction import extract_features

# --------------- CONFIG --------------- #
FEEDBACK_FILE = "DATA/feedbackreview.txt"
REVIEW_LOG = "DATA/review.csv"
YOUR_EMAIL = "abhi.s.khanzode@gmail.com"
YOUR_PASSWORD = "ahlx zipv mbzi qmzb"
MODEL_PATH = "FINAL_MODEL/phishing_model.pkl"
# ------------------------------------- #

# 🔹 Load model once
model = joblib.load(MODEL_PATH)

import csv
import os

def add_to_false_positive(url):
    file_path = "CSV/false_positive.csv"

    # File initialize with header if not exists
    if not os.path.exists(file_path):
        with open(file_path, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["url", "label"])

    # Append the safe URL
    with open(file_path, "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([url, 0])

    print(f"✅ Added to false_positive.csv: {url},0")

# 🔹 Send Email
def send_email(to_email, url, verdict):
    message = f"""Hi, 

Thank you for submitting the website for review:
🔗 {url}

After detailed analysis, these website is marked as: {verdict.upper()}.

Please stay alert and avoid sharing any sensitive information.

— ABHI Shield Team 🛡
"""
    msg = MIMEText(message)
    msg["Subject"] = "🔐 Final Website Review - ABHI-Shield"
    msg["From"] = YOUR_EMAIL
    msg["To"] = to_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(YOUR_EMAIL, YOUR_PASSWORD)
            server.send_message(msg)
        print("✅ Email sent to", to_email)
    except Exception as e:
        print("❌ Email Error:", e)

# 🔹 Model prediction
def model_predict(url):
    try:
        features = extract_features(url)
        df = pd.DataFrame([features])
        prediction = model.predict(df)[0]
        confidence = model.predict_proba(df)[0][prediction] * 100
        verdict = "true" if prediction == 1 else "false"
        print(f"🤖 Model Review: {'Its ⚠ Phishing site..!!' if prediction == 1 else '🔒Its Safe Site.'} (Confidence: {confidence:.2f}%)")
        return verdict
    except Exception as e:
        print("❌ Model error:", e)
        return "unknown"


def get_all_feedbacks():
    with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
        lines = f.read().strip().split("\n")

    feedbacks = []
    current = {}
    for line in lines:
        if line.startswith("Name"):
            current["name"] = line.split(":", 1)[1].strip()
        elif line.startswith("Email"):
            current["email"] = line.split(":", 1)[1].strip()
        elif line.startswith("URL"):
            current["url"] = line.split(":", 1)[1].strip()
        elif line.startswith("Issue"):
            current["issue"] = line.split(":", 1)[1].strip()
        elif line.startswith("-"):
            # Only add if all required keys are present
            if all(k in current for k in ("name", "email", "url", "issue")):
                feedbacks.append(current)
            else:
                print("⚠ Skipping incomplete entry:", current)
            current = {}
    return feedbacks

# 🔹 Log results
def log_result(url, model_result, human_result):
    with open(REVIEW_LOG, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(), url, model_result, human_result])

# 🔹 Review logic
def review_process():
    feedbacks = get_all_feedbacks()
    if not feedbacks:
        print("⚠ No feedback data found.")
        return

    print("\n📋 Available Feedback Entries:")
    for idx, fb in enumerate(feedbacks, start=1):
        print(f"{idx}. {fb['name']} - {fb['email']} - {fb['url']}")

    try:
        choice = int(input("\n🔎 Enter the number you want to review: ")) - 1
        selected = feedbacks[choice]
    except:
        print("❌ Invalid choice.")
        return

    print("\n📩 Selected Entry:")
    print("Name :", selected["name"])
    print("Email:", selected["email"])
    print("URL  :", selected["url"])
    print("Issue:", selected["issue"])
    print("-" * 40)

    url = selected["url"]
    email = selected["email"]

    # Step 1: ML model
    model_result = model_predict(url)
    if model_result == "unknown":
        return

    choice = input("Do you want to continue with human review? (y/n): ").strip().lower()
    if choice != "y":
        log_result(url, model_result, model_result)
        send_email(email, url, "Phishing" if model_result == "true" else "Safe")
        print("✅ Finalized using ML result only.")
        return

    # Step 2: Human review
    human_verdict = input("👤 Enter your verdict for this URL (true for phishing / false for safe): ").strip().lower()
    print(f"Model result: {model_result}, Human verdict: {human_verdict}")


    confirm = input("📨 Do you want to send email to user? (y/n): ").strip().lower()
    if confirm == "y":
        send_email(email, url, "Phishing" if human_verdict == "true" else "Safe")
    else:
        print("ℹ Email not sent.")

    log_result(url, model_result, human_verdict)

    if model_result.lower() == "false" and human_verdict.lower() == "false":
        add_to_false_positive(url)
    
    print("✅ Review process completed.")




# Run

if __name__ == "__main__":
    review_process()                            