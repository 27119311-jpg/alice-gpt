from flask import Flask, request, jsonify
import os
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/", methods=["POST"])
def alice():
    data = request.json

    user_text = data["request"]["original_utterance"]

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "user", "content": user_text}
            ]
        )

        answer = response.choices[0].message.content

    except Exception as e:
        print(e)
        answer = "Ошибка при обращении к GPT"

    return jsonify({
        "version": data["version"],
        "response": {
            "text": answer,
            "end_session": False
        }
    })
