import openai
import os

# ✅ API Key (use env var in production)
OPENAI_API_KEY = "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"

# ✅ Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# ✅ Default log path
CHAT_LOG_PATH = "DATA/chat_log.txt"

def ensure_chat_log_exists():
    os.makedirs("DATA", exist_ok=True)
    if not os.path.exists(CHAT_LOG_PATH):
        with open(CHAT_LOG_PATH, "w") as f:
            f.write("You: Hello\nABHI: Hello! I'm ABHI, your cyber assistant.\n")

# ✅ Generate a reply from GPT
def generate_reply(question):
    ensure_chat_log_exists()

    # Read previous log
    with open(CHAT_LOG_PATH, "r") as f:
        chat_log = f.read()

    # Prepare prompt
    prompt = f"{chat_log}\nYou: {question}\nABHI:"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=100,
            top_p=0.8,
            frequency_penalty=0.5,
            presence_penalty=0.3
        )

        answer = response.choices[0].message.content.strip()

        # Update chat log
        updated_log = chat_log + f"\nYou: {question}\nABHI: {answer}"
        with open(CHAT_LOG_PATH, "w") as f:
            f.write(updated_log)

        return answer

    except Exception as e:
        print("❌ GPT Error:", e)
        return "Sorry, ABHI is facing a technical issue right now."

