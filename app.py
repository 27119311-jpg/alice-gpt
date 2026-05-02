from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


@app.route("/", methods=["GET"])
def health_check():
    return "Alice GPT server is running"


@app.route("/", methods=["POST"])
def alice():
    data = request.json or {}

    user_text = data.get("request", {}).get("original_utterance", "")

    if not user_text:
        answer = "Привет! Я GPT-помощник. Задай мне вопрос."
    else:
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {
                            "role": "system",
                            "content": "Ты полезный голосовой помощник. Отвечай кратко, понятно и по-русски."
                        },
                        {
                            "role": "user",
                            "content": user_text
                        }
                    ],
                    "temperature": 0.7
                },
                timeout=20
            )

            result = response.json()
            answer = result["choices"][0]["message"]["content"]

        except Exception:
            answer = "Извини, сейчас не получилось получить ответ от GPT. Попробуй ещё раз."

    return jsonify({
        "version": "1.0",
        "response": {
            "text": answer,
            "tts": answer,
            "end_session": False
        }
    })
