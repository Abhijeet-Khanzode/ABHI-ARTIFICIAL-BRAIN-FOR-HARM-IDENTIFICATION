import openai
import os
import traceback


# ✅ API Key (use env var in production)
client = openai.OpenAI("OPENAI_API_KEY")
OPENAI_API_KEY = os.environ.get()
if not OPENAI_API_KEY:
    raise ValueError("❌ No OPENAI_API_KEY found in environment variables!")

# ✅ Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# ✅ Default log path
CHAT_LOG_DIR = os.path.join("ABHI", "DATA")

CHAT_LOG_PATH = os.path.join(CHAT_LOG_DIR, "chat_log.txt")

def ensure_chat_log_exists():
    os.makedirs(CHAT_LOG_DIR, exist_ok=True)
    if not os.path.exists(CHAT_LOG_PATH):
        with open(CHAT_LOG_PATH, "w") as f:
            f.write("You: Hello\nABHI: Hello! I'm ABHI, your cyber assistant.\n")

# ✅ Generate a reply from GPT
def generate_reply(question: str) -> str:
    ensure_chat_log_exists()

    # Read previous log
    with open(CHAT_LOG_PATH, "r") as f:
        chat_log = f.read()

    # Prepare prompt
    prompt = f"{chat_log}\nYou: {question}\nABHI:"
    try:
        response = client.chat.completions.create(
        model="gpt-4o-mini",   # ✅ Fast + cheap model
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=100,
        top_p=0.8,
        frequency_penalty=0.5,
        presence_penalty=0.3
    )

        answer = response.choices[0].message.content.strip()


        # Update chat log
            # Update chat log
        updated_log = chat_log + f"\nYou: {question}\nABHI: {answer}"
        with open(CHAT_LOG_PATH, "w") as f:
            f.write(updated_log)

        return answer


    except Exception as e:
        print("❌ GPT Error:", e)
        traceback.print_exc()
        return "Sorry, ABHI is facing a technical issue right now."




