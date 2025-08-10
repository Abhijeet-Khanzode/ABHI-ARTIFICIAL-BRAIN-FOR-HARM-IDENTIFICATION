import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from feature_extraction import extract_features
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

def safe_extract(url):
    try:
        return extract_features(str(url))
    except Exception as e:
        print(f"⚠️ Skipped URL: {url} -> {e}")
        return None

def retrain_model():
    try:
        print("📥 Loading datasets...")

        # ✅ Verified phishing URLs
        phishing_df = pd.read_csv("CSV/verified_online.csv")[["url"]].dropna()
        phishing_df["label"] = 1

        # ✅ Safe URLs
        safe_df = pd.read_csv("CSV/safe_10000.csv")[["url", "label"]]
        slug_df = pd.read_csv("CSV/safe_slug_50000.csv")[["url", "label"]]

        # ✅ False positives from feedback
        feedback_df = pd.read_csv("CSV/false_positive.csv").dropna()
        if "label" not in feedback_df.columns or feedback_df["label"].isnull().any():
            feedback_df["label"] = 0
        else:
            feedback_df["label"] = feedback_df["label"].astype(int)
        print("📝 Feedback data (false positives):")
        print(feedback_df.head())
        print("👉 Total feedback entries:", len(feedback_df))

        # ✅ Additional datasets (optional)
        legit_new = pd.read_csv("CSV/legitimate_url.csv").dropna()
        legit_new = legit_new.rename(columns={"type": "label"})
        legit_new["label"] = 0

        phish_new = pd.read_csv("CSV/phishing_url.csv").dropna()
        phish_new = phish_new.rename(columns={"type": "label"})
        phish_new["label"] = 1

        # ✅ Combine all data
        combined_df = pd.concat([
            phishing_df,
            safe_df,
            slug_df,
            feedback_df[["url", "label"]],
            legit_new[["url", "label"]],
            phish_new[["url", "label"]]
        ], ignore_index=True).dropna(subset=["url"]).drop_duplicates(subset="url")

        print(f"🔢 Total combined URLs: {len(combined_df)}")

        # ✅ Feature extraction
        print("🧠 Extracting features...")
        X_raw = combined_df["url"].apply(safe_extract)
        X = X_raw.dropna().apply(pd.Series)
        y = combined_df.loc[X.index, "label"]

        expected_features = [
            "url_length", "has_https", "has_at_symbol", "has_ip", "has_dash",
            "num_dots", "is_shortened", "has_login_keyword", "subdomain_depth",
            "is_known_safe_domain"
        ]

        missing = set(expected_features) - set(X.columns)
        if missing:
            raise ValueError(f"❌ Missing required features: {missing}")

        X = X[expected_features]

        if X.empty or y.empty:
            print("❌ Not enough data to train. Aborting.")
            return

        # ✅ Split & train
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, stratify=y, random_state=42)

        print("🚀 Training XGBoost model...")
        model = XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            use_label_encoder=False,
            eval_metric='logloss'
        )
        model.fit(X_train, y_train)

        # ✅ Save model
        joblib.dump(model, "FINAL_MODEL/phishing_model.pkl")
        print("✅ Model retrained and saved as phishing_model.pkl")
        y_pred = model.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        print(f"✅ Model Accuracy: {acc * 100:.2f}%")


        print("🎯 Classification Report:\n")
        print(classification_report(y_test, y_pred))

        print("📊 Confusion Matrix:\n")
        print(confusion_matrix(y_test, y_pred))

    except Exception as e:
        print("❌ Error during retraining:", e)

if __name__ == "__main__":
    retrain_model()


