from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
sys.path.append('./Rusty')
from Rusty.main import process_text

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
        result = process_text(input_text)
        # Always read the summary from output_final_summary.txt after processing
        try:
            with open('output_final_summary.txt', 'r') as f:
                output = f.read().strip()
        except Exception as file_err:
            output = f"[Error reading summary file: {file_err}]"
        if not output:
            output = "No credible summary generated."
        return jsonify({"output": output})
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
