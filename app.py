from flask import Flask, request, jsonify
import os
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route("/", methods=["POST"])
def webhook():
    data = request.json

    user_text = data["request"]["original_utterance"]

    try:
        response = client.responses.create(
    model="gpt-4.1-mini",
    input=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": user_text}
            ]
        }
    ]
        )
        answer = response.output[0].content[0].text

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
