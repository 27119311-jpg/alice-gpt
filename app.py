from flask import Flask, request, jsonify
import os
import time
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

memory = {}
MEMORY_TTL = 15 * 60
MAX_MESSAGES = 20


def get_user_id(data):
    return (
        data.get("session", {}).get("user_id")
        or data.get("session", {}).get("application", {}).get("application_id")
        or "default_user"
    )


@app.route("/", methods=["POST"])
def webhook():
    data = request.json or {}

    user_id = get_user_id(data)
    user_text = data.get("request", {}).get("original_utterance", "").strip()

    if not user_text:
        user_text = "Привет"

    now = time.time()

    user_memory = memory.get(user_id, {"updated_at": now, "messages": []})

    if now - user_memory["updated_at"] > MEMORY_TTL:
        user_memory = {"updated_at": now, "messages": []}

    messages = user_memory["messages"]

    messages.append({
        "role": "user",
        "content": user_text
    })

    messages = messages[-MAX_MESSAGES:]

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Ты полезный голосовой помощник. Отвечай по-русски, кратко и понятно."
                }
            ] + messages
        )

        answer = response.choices[0].message.content

    except Exception as e:
        answer = "Ошибка: " + str(e)

    messages.append({
        "role": "assistant",
        "content": answer
    })

    messages = messages[-MAX_MESSAGES:]

    memory[user_id] = {
        "updated_at": now,
        "messages": messages
    }

    return jsonify({
        "response": {
            "text": answer,
            "end_session": False
        },
        "version": "1.0"
    })


@app.route("/", methods=["GET"])
def index():
    return "Alice GPT server is running"
