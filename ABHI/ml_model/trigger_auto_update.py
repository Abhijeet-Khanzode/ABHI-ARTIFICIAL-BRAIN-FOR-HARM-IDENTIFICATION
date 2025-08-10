import subprocess

def trigger_auto_update():
    try:
        print("🔁 Starting auto model retraining...")
        subprocess.Popen(["python", "auto_update_model.py"])
        print("✅ Auto update triggered.")
    except Exception as e:
        print("❌ Failed to trigger model update:", e)