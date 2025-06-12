import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS  
import subprocess
from db.db_setup import create_db_with_scenarios
import logging

from utils.app_log import setup_logging
from utils.config_loader import load_config
from utils.log_clean import manage_log_files
from utils.arrange_scenario import rename_scenarios
from runners.scenario_runner import run_all_db_scenarios


app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(__file__)
ASSETS_FOLDER = os.path.join(BASE_DIR, '..', 'assets')
SCENARIOS_FOLDER = os.path.join(BASE_DIR, '..', 'scenarios')
DB_PATH = os.path.join(SCENARIOS_FOLDER, 'scenario.db')  # ✅ DB 경로
MAIN_SCRIPT = os.path.join(BASE_DIR, '..', 'main.py')

os.makedirs(ASSETS_FOLDER, exist_ok=True)
os.makedirs(SCENARIOS_FOLDER, exist_ok=True)

def pos_to_str(pos):
    if isinstance(pos, list):
        return ",".join(map(str, pos))
    return pos

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
    import re
    steps = request.json

    try:
        existing_files = os.listdir(SCENARIOS_FOLDER)
        db_files = [f for f in existing_files if re.match(r"\d+_scenario\.db$", f)]
        next_index = 1
        if db_files:
            numbers = [int(f.split("_")[0]) for f in db_files]
            next_index = max(numbers) + 1

        new_db_filename = f"{next_index}_scenario.db"
        new_db_path = os.path.join(SCENARIOS_FOLDER, new_db_filename)

        # db_loader의 함수 호출
        create_db_with_scenarios(new_db_path, steps)

        return jsonify({"status": "saved", "db": new_db_filename})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/run", methods=["POST"])
def run():
    result = subprocess.run(["python", MAIN_SCRIPT], capture_output=True, text=True)
    return jsonify({
        "stdout": result.stdout,
        "stderr": result.stderr
    })

@app.route("/run-scenario", methods=["POST"])
def run_scenario():
    setup_logging()
    manage_log_files()
    config = load_config("config/config.yaml")
    logging.info("자동화 툴 시작")
    rename_scenarios()

    run_all_db_scenarios(config)

    logging.info("[MAIN] 모든 시나리오 실행 완료")
    return jsonify({"status": "success", "message": "모든 시나리오 실행 완료"})

if __name__ == "__main__":
    app.run(port=5000)

