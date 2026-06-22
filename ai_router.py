import os
import requests

# ===============================
# API KEYS (FROM .env)
# ===============================
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ===============================
# VECNA CHARACTER PROMPT
# (Can be moved to Vecna_prompts.py later)
# ===============================
VECNA_PROMPT = """
You are Vecna.
You are not an assistant.
You are a presence.
You speak slowly, calmly, and with menace.
You explain as if the listener is already trapped.
"""

# ===============================
# GOOGLE AI (PRIMARY)
# ===============================
def ask_google_ai(user_input):
    url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": GOOGLE_API_KEY}

    payload = {
        "contents": [{
            "parts": [{"text": VECNA_PROMPT + "\nUser: " + user_input}]
        }]
    }

    response = requests.post(
        url, headers=headers, params=params, json=payload, timeout=15
    )

    if response.status_code != 200:
        raise Exception("Google AI limit or error")

    return response.json()["candidates"][0]["content"]["parts"][0]["text"]

# ===============================
# OPENROUTER (SECONDARY)
# ===============================
def ask_openrouter(user_input):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "meta-llama/llama-3.1-8b-instruct",
        "messages": [
            {"role": "system", "content": VECNA_PROMPT},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=payload, timeout=15)

    if response.status_code != 200:
        raise Exception("OpenRouter error")

    return response.json()["choices"][0]["message"]["content"]

# ===============================
# GROQ (THIRD FALLBACK – FAST)
# ===============================
def ask_groq(user_input):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": VECNA_PROMPT},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=payload, timeout=15)

    if response.status_code != 200:
        raise Exception("Groq error")

    return response.json()["choices"][0]["message"]["content"]

# ===============================
# AI ROUTER (AUTO FAILOVER)
# ===============================
def ask_vecna(user_input):
    try:
        print("🧠 Using Google AI")
        return ask_google_ai(user_input)
    except Exception:
        try:
            print("🧠 Google failed → Using OpenRouter")
            return ask_openrouter(user_input)
        except Exception:
            print("🧠 OpenRouter failed → Using Groq")
            return ask_groq(user_input)
