from flask import Flask, request, jsonify,render_template
from flask_cors import CORS
import joblib
import pandas as pd
from urllib.parse import urlparse
from feature_extraction import extract_features  # your 7-feature extractor
from colorama import Fore
import subprocess
from trigger_auto_update import trigger_auto_update
from auto_update_model import retrain_model
from feature_extraction import KNOWN_SAFE_DOMAINS  # import it from feature_extraction.py
from ai_brain import generate_reply
import re
from email_send import send_thank_you_email
from waitress import serve
import os
import xgboost as xgb
from db import init_db, insert_feedback_review, insert_review

print(Fore.GREEN,Fore.RED+""" 



      
░█████╗░██████╗░██╗░░██╗██╗
██╔══██╗██╔══██╗██║░░██║██║
███████║██████╦╝███████║██║
██╔══██║██╔══██╗██╔══██║██║
██║░░██║██████╦╝██║░░██║██║
╚═╝░░╚═╝╚═════╝░╚═╝░░╚═╝╚═╝( Artificial Brain for Harm Identification)
                           
      
     \n """)
app = Flask(__name__)
CORS(app)

#model = joblib.load("ABHI/FINAL_MODEL/phishing_model.pkl")
booster = xgb.Booster()
booster.load_model("ABHI/FINAL_MODEL/phishing_model.json")

SENDER_EMAIL = "abhi.s.khanzode@gmail.com"
SENDER_PASSWORD = "ahlx zipv mbzi qmzb" 


def load_false_positives(path="ABHI/CSV/false_positive.csv"):
    try:
        df = pd.read_csv(path, names=["url", "label"])
        return set(df["url"].dropna().str.strip())
    except Exception as e:
        print(f"❌ Error loading false positives: {e}")
        return set()

FALSE_POSITIVES = load_false_positives()

init_db()

@app.route("/", methods=["GET"])
def home():
    return """
    <html>
    <head>
        <title>ABHI - Artificial Brain for Harm Identification</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                background-color: #121212;
                color: #ffffff;
                padding: 30px;
            }
            .logo {
                font-family: monospace;
                white-space: pre;
                font-size: 14px;
                color: #00FF00;
                margin-bottom: 20px;
            }
            .card {
                background: #1e1e1e;
                border-radius: 15px;
                padding: 20px;
                margin: auto;
                max-width: 700px;
                box-shadow: 0 0 15px rgba(0,255,0,0.3);
                text-align: left;
            }
            h1 {
                text-align: center;
                color: #00ffcc;
            }
            a {
                color: #00ffcc;
                text-decoration: none;
                font-weight: bold;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="logo">
        ░█████╗░██████╗░██╗░░██╗██╗
        ██╔══██╗██╔══██╗██║░░██║██║
        ███████║██████╦╝███████║██║
        ██╔══██║██╔══██╗██╔══██║██║
        ██║░░██║██████╦╝██║░░██║██║
        ╚═╝░░╚═╝╚═════╝░╚═╝░░╚═╝╚═╝
        <br>(Artificial Brain for Harm Identification)
        </div>

        <div class="card">
            <h1>About the Extension</h1>
            <p>
                This browser extension helps in detecting harmful and phishing content online 
                using our AI-powered Artificial Brain for Harm Identification. 
            </p>

            <h2>🚀 Features</h2>
            <ul>
                <li>Phishing website detection</li>
                <li>Content analysis & warnings</li>
                <li>Human + AI double review</li>
                <li>Automatic email alerts</li>
            </ul>

            <h2>📥 Download & Install</h2>
            <ol>
                <li>Download the extension from <a href="https://github.com/Abhijeet-Khanzode/ABHI-ARTIFICIAL-BRAIN-FOR-HARM-IDENTIFICATION-CLIENT">GitHub Repository</a></li>
                <li>Go to your browser's extensions page (<b>chrome://extensions</b> in Chrome).</li>
                <li>Enable <b>Developer Mode</b>.</li>
                <li>Click on <b>Load Unpacked</b> and select the extension folder.</li>
                <li>Done ✅, extension will be active.</li>
            </ol>

            <h2>📖 Usage</h2>
            <p>
                Once installed, the extension automatically scans websites you visit and 
                shows warnings if suspicious activity is detected. You can also 
                submit suspicious URLs for manual review.
            </p>

            <h2>👨‍💻 Developer</h2>
            <p>Created by <b>Abhijeet Khanzode</b><br>
            <a href="http://github.com/Abhijeet-Khanzode">GitHub Profile</a></p>
        </div>
    </body>
    </html>
    """
@app.route("/check", methods=["POST"])
def check_url():
    try:
        data = request.get_json()
        url = data.get("url", "")
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()

        # ⛔ Ignore browser or localhost URLs
        if parsed.scheme.startswith("chrome") or "localhost" in domain:
            return jsonify({"isPhishing": False, "confidence": 0.0})

        # ✅ Bypass known safe domains that are just browsing (no login keywords)
        if any(d in domain for d in KNOWN_SAFE_DOMAINS) and not any(p in path for p in ["login", "signin", "verify", "auth"]):
            return jsonify({
                "isPhishing": False,
                "confidence": 55.56,
                "reason": "Browsing on known safe domain"
            })

        if url.strip() in FALSE_POSITIVES:
            print("✅ URL found in false positives. Marked safe.")
            return jsonify({"isPhishing": False, "confidence": 0.0})

        # 🔍 Extract features and predict
        features = extract_features(url)
        feature_df = pd.DataFrame([features])

        dmat = xgb.DMatrix(feature_df)
        proba = float(booster.predict(dmat)[0])  # returns probability of class 1 (phishing)

        prediction = 1 if proba > 0.5 else 0
        
        return jsonify({
            "isPhishing": bool(prediction),
            "confidence": round(proba * 100, 2)
        })

    except Exception as e:
        return jsonify({"isPhishing": False, "error": str(e)}), 500
    
# @app.route("/feedback-review", methods=["POST"])
# def review_feedback():
#     data = request.get_json()
#     if not data:
#         return jsonify({"status": "error", "message": "No data provided"}), 400

#     name = data.get("name", "N/A")
#     email = data.get("email", "N/A")
#     url = data.get("url", "N/A")
#     issue = data.get("issue", "N/A")

#     try:
#         with open("ABHI/DATA/feedbackreview.txt", "a", encoding="utf-8") as f:
#             f.write(f"📝 Feedback Received:\n")
#             f.write(f"Name  : {name}\n")
#             f.write(f"Email : {email}\n")
#             f.write(f"URL   : {url}\n")
#             f.write(f"Issue : {issue}\n")
#             f.write(f"{'-'*40}\n")    
            
#         send_thank_you_email(email, name, url)
        
#         return jsonify({"status": "success", "message": "Feedback recevied email sent"}), 200

#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/feedback-review", methods=["POST"])
def review_feedback():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400

    name = data.get("name", "N/A")
    email = data.get("email", "N/A")
    url = data.get("url", "N/A")
    issue = data.get("issue", "N/A")

    try:
        # ✅ DB me save karna
        insert_feedback_review(name, email, url, issue)

        # ✅ Email bhejna
        send_thank_you_email(email, name, url)

        return jsonify({"status": "success", "message": "Feedback received & email sent"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# @app.route('/feedback', methods=['POST'])
# def feedback():
#     try:
#         data = request.get_json()
#         url = data.get("url", "")
#         feedback_type = data.get("feedback", "")

#         print("🧠 Feedback Triggered")
#         print("Received:", url, feedback_type)

#         if feedback_type == "false_positive":
#             with open("ABHI/CSV/review.csv", "a") as f:
#                 f.write(f"{url},0\n")  # 🟢 Correct format
#             print("✅ Written to review.csv")

        # # trigger_auto_update() 
        # retrain_model()
        # global model
        # model = joblib.load("ml_model/phishing_model.pkl")
        # print("✅ Model reloaded after training.")
        return jsonify({"success": True})
            
    # except Exception as e:
    #     print(f"❌ Feedback Error: {e}")
    #     return jsonify({"success": False, "error": str(e)}), 500

@app.route('/feedback', methods=['POST'])
def feedback():
    try:
        data = request.get_json()
        url = data.get("url", "")
        feedback_type = data.get("feedback", "")

        print("🧠 Feedback Triggered")
        print("Received:", url, feedback_type)

        if feedback_type == "false_positive":
            # ✅ DB me save karna (review.csv ka replacement)
            insert_review(url, 0)
            print("✅ Written to review table")

        return jsonify({"success": True})

    except Exception as e:
        print(f"❌ Feedback Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/respond", methods=["POST"])
def respond():
        data = request.get_json()
        msg = data.get("message", "")
        # msg = "hi"
        print(f"💬 User: {msg}")
        reply = generate_reply(msg)
        return jsonify({"reply": reply})


if __name__ == "__main__":
      port = int(os.environ.get("PORT", 5000))
      serve(app, host="0.0.0.0", port=port)


