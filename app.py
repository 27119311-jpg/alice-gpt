from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

@app.route("/", methods=["POST"])
def alice():
    data = request.json
    user_text = data["request"]["original_utterance"]

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": user_text}]
        }
    )

    answer = response.json()["choices"][0]["message"]["content"]

    return jsonify({
        "response": {
            "text": answer,
            "end_session": False
        },
        "version": "1.0"
    })
