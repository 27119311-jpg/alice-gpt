from flask import Flask, request, jsonify
import os
import time
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ⚙️ Настройки памяти
memory = {}
MEMORY_TTL = 15 * 60   # 15 минут
MAX_MESSAGES = 20      # максимум 20 сообщений


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

    # Берём память пользователя
    user_memory = memory.get(user_id, {"updated_at": now, "messages": []})

    # Если прошло больше 15 минут — очищаем
    if now - user_memory["updated_at"] > MEMORY_TTL:
        user_memory = {"updated_at": now, "messages": []}

    messages = user_memory["messages"]

    # Добавляем сообщение пользователя
    messages.append({
        "role": "user",
        "content": user_text
    })

    # Оставляем только последние 20 сообщений
    messages = messages[-MAX_MESSAGES:]

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=messages
        )

        answer = ""

        for item in response.output:
            for content in item.content:
                if hasattr(content, "text"):
                    answer += content.text

        if not answer:
            answer = "Не удалось получить ответ"

    except Exception as e:
        answer = "Ошибка: " + str(e)

    # Добавляем ответ ассистента в память
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
