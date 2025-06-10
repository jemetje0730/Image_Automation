from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS  
import os
import json
import subprocess

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(__file__)
ASSETS_FOLDER = os.path.join(BASE_DIR, '..', 'assets')
SCENARIOS_FOLDER = os.path.join(BASE_DIR, '..', 'scenarios')
MAIN_SCRIPT = os.path.join(BASE_DIR, '..', 'main.py')

os.makedirs(ASSETS_FOLDER, exist_ok=True)
os.makedirs(SCENARIOS_FOLDER, exist_ok=True)

@app.route("/upload-image", methods=["POST"])
def upload_image():
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    save_path = os.path.join(ASSETS_FOLDER, file.filename)
    file.save(save_path)

    return jsonify({"filename": file.filename})

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory(ASSETS_FOLDER, filename)

@app.route("/save-scenario", methods=["POST"])
def save_scenario():
    scenario = request.json
    existing = [f for f in os.listdir(SCENARIOS_FOLDER) if f.endswith('_scenario.json')]
    nums = [int(f.split('_')[0]) for f in existing if f.split('_')[0].isdigit()]
    next_num = max(nums) + 1 if nums else 1
    save_path = os.path.join(SCENARIOS_FOLDER, f"{next_num}_scenario.json")
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(scenario, f, indent=2, ensure_ascii=False)
    return jsonify({"status": "saved", "filename": save_path})


@app.route("/run", methods=["POST"])
def run():
    result = subprocess.run(["python", MAIN_SCRIPT], capture_output=True, text=True)
    return jsonify({
        "stdout": result.stdout,
        "stderr": result.stderr
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
