from flask import Flask, request, jsonify
from flask_cors import CORS  
import os
import json
import subprocess

app = Flask(__name__)
CORS(app)

ASSETS_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'assets')
SCENARIO_PATH = os.path.join(os.path.dirname(__file__), '..', 'scenarios', '1_scenario.json')
MAIN_SCRIPT = os.path.join(os.path.dirname(__file__), '..', 'main.py')

@app.route("/upload-image", methods=["POST"])
def upload_image():
    file = request.files['file']
    save_path = os.path.join(ASSETS_FOLDER, file.filename)
    file.save(save_path)
    return jsonify({"filename": file.filename})

@app.route("/save-scenario", methods=["POST"])
def save_scenario():
    scenario = request.json
    with open(SCENARIO_PATH, "w", encoding="utf-8") as f:
        json.dump(scenario, f, indent=2, ensure_ascii=False)
    return jsonify({"status": "saved"})

@app.route("/run", methods=["POST"])
def run():
    scenario = request.json
    with open(SCENARIO_PATH, "w", encoding="utf-8") as f:
        json.dump(scenario, f, indent=2, ensure_ascii=False)

    result = subprocess.run(["python", MAIN_SCRIPT], capture_output=True, text=True)
    return jsonify({
        "stdout": result.stdout,
        "stderr": result.stderr
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
