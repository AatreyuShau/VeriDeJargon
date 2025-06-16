from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
sys.path.append('./Rusty')
from Rusty.main import process_text
from Rusty.research_pipeline import process_research_topic

app = Flask(__name__)
CORS(app)  # Enable CORS so JS from file:// or other origins can talk to Flask

@app.route('/process', methods=['POST'])
def process_text_route():
    data = request.get_json()
    input_text = data.get("text", "")
    if not input_text.strip():
        return jsonify({"output": "⚠️ No input text provided."})
    try:
        # Use the Rusty/main.py process_text function
        summary, definitions = process_text(input_text, return_definitions=True)
        return jsonify({"summary": summary, "definitions": definitions})
    except Exception as e:
        return jsonify({"output": f"Error: {str(e)}"})

@app.route('/research', methods=['POST'])
def research_route():
    data = request.get_json()
    topic = data.get("topic", "")
    if not topic.strip():
        return jsonify({"output": "⚠️ No research topic provided."})
    try:
        # Use a new research pipeline for structured research output
        result = process_research_topic(topic)
        return jsonify(result)
    except Exception as e:
        return jsonify({"output": f"Error: {str(e)}"})

@app.route('/')
def index():
    return send_from_directory('.', 'main.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
