from flask import Flask, render_template, request, jsonify
import subprocess
import requests,json,markdown
from bs4 import BeautifulSoup
app = Flask(__name__)

# Global variable to store the process running the LLMs
# llm_process = None

url = "http://localhost:11434/api/generate"

headers = {
    'Content-Type': 'application/json',
}

conversation_history = []


@app.route('/conversation-history',methods=['GET'])
def get_conversation():
    return jsonify({'conversation_history': conversation_history})

@app.route('/generate-response', methods=['POST'])
def generate_response():
    data = request.get_json()
    prompt = data['prompt']
    conversation_history.append(prompt)

    full_prompt = "\n".join(conversation_history)

    data = {
        "model": "gemma:2b",
        "stream": False,
        "prompt": full_prompt,
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_text = response.text
        data = json.loads(response_text)
        actual_response = data["response"]
        conversation_history.append(actual_response)
        html = markdown.markdown(actual_response)
    
        # Strip HTML tags to get plain text
        plain_text = ''.join(BeautifulSoup(html, "html.parser").findAll(text=True))
        print(plain_text)
        return jsonify({'response': plain_text})
    else:
        print("Error:", response.status_code, response.text)
        return None


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
