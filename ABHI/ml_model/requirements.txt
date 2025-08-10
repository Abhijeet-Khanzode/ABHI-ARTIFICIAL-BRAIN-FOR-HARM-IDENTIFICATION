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

model = joblib.load("FINAL_MODEL/phishing_model.pkl")

SENDER_EMAIL = "abhi.s.khanzode@gmail.com"
SENDER_PASSWORD = "ahlx zipv mbzi qmzb" 


def load_false_positives(path="CSV/false_positive.csv"):
    try:
        df = pd.read_csv(path, names=["url", "label"])
        return set(df["url"].dropna().str.strip())
    except Exception as e:
        print(f"❌ Error loading false positives: {e}")
        return set()

FALSE_POSITIVES = load_false_positives()


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
        prediction = model.predict(feature_df)[0]
        proba = float(model.predict_proba(feature_df)[0][1])  # probability of phishing

        return jsonify({
            "isPhishing": bool(prediction),
            "confidence": round(proba * 100, 2)
        })

    except Exception as e:
        return jsonify({"isPhishing": False, "error": str(e)}), 500
    
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
        with open("DATA/feedbackreview.txt", "a", encoding="utf-8") as f:
            f.write(f"📝 Feedback Received:\n")
            f.write(f"Name  : {name}\n")
            f.write(f"Email : {email}\n")
            f.write(f"URL   : {url}\n")
            f.write(f"Issue : {issue}\n")
            f.write(f"{'-'*40}\n")    
            
        send_thank_you_email(email, name, url)
        
        return jsonify({"status": "success", "message": "Feedback recevied email sent"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/feedback', methods=['POST'])
def feedback():
    try:
        data = request.get_json()
        url = data.get("url", "")
        feedback_type = data.get("feedback", "")

        print("🧠 Feedback Triggered")
        print("Received:", url, feedback_type)

        if feedback_type == "false_positive":
            with open("CSV/review.csv", "a") as f:
                f.write(f"{url},0\n")  # 🟢 Correct format
            print("✅ Written to review.csv")

        # # trigger_auto_update() 
        # retrain_model()
        # global model
        # model = joblib.load("ml_model/phishing_model.pkl")
        # print("✅ Model reloaded after training.")
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




