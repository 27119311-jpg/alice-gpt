from flask import Flask, request, jsonify
import os
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route("/", methods=["POST"])
def webhook():
    data = request.json

    user_text = data.get("request", {}).get("original_utterance", "")

    if not user_text:
        user_text = "Привет"

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=user_text
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

    return jsonify({
        "response": {
            "text": answer,
            "end_session": False
        },
        "version": "1.0"
    })

@app.route("/", methods=["GET"])
def index():
    return "OK"
