# import requests
# res = requests.post("http://localhost:5000/feedback", json={
#     "url": "https://www.google.com/search?q=superset",
#     "feedback": "false_positive"
# })
# print(res.json())


# import requests
# res = requests.post("http://localhost:5000/check", json={"url": "https://www.github.com"})
# print(res.json())
# from feature_extraction import extract_features
# import joblib
# import pandas as pd
# import  pickle

# model = joblib.load("ml_model/phishing_model.pkl")
# # model = pickle.load(open("ml_model/XGBoostClassifier.pickle", "rb"))
# urls = [
#     "https://www.google.com",
#     "https://joinsuperset.com/",
#     "https://secure-verification-paypal.com",
#     "https://chatgpt.com/"
# ]

# for url in urls:
#     x = pd.DataFrame([extract_features(url)])
#     pred = model.predict(x)[0]
#     prob = model.predict_proba(x)[0][1]
#     print(f"🔗 {url}\n ➤ {'Phishing' if pred==1 else 'Safe'} | Confidence: {prob*100:.2f}%\n")
import joblib
import pandas as pd
from feature_extraction import extract_features

# Load the trained model
model = joblib.load("FINAL_MODEL/phishing_model.pkl")

# Test URLs
test_urls = [

    "https://login-microsoft-secure.com"

]

print("\n🔍 Testing ABHI AI Model...\n")

for url in test_urls:
    try:
        features = extract_features(url)
        df = pd.DataFrame([features])

        prediction = model.predict(df)[0]
        confidence = model.predict_proba(df)[0][prediction] * 100

        status = "🔒 Safe" if prediction == 0 else "⚠️ Phishing"
        print(f"🔗 {url}\n   ➤ {status} | Confidence: {confidence:.2f}%\n")

    except Exception as e:
        print(f"❌ Error testing {url}: {e}")
