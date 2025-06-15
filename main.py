from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
sys.path.append('./Rusty')
from Rusty.pipeline import Pipeline

app = Flask(__name__)
CORS(app)  # Enable CORS so JS from file:// or other origins can talk to Flask

@app.route('/process', methods=['POST'])
def process_text():
    data = request.get_json()
    input_text = data.get("text", "")

    processed_text = refine_text(input_text)

    return jsonify({"output": processed_text})

def refine_text(text):
    text = text.strip()
    if not text:
        return "⚠️ No input text provided."
    try:
        pipeline = Pipeline()
        result = pipeline.run(text)
        if isinstance(result, str):
            return result
        return "\n".join([f"{line} (conf: {conf:.2f})" for line, conf in result])
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True, port=5000)
