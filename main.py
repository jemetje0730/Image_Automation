# main.py

import os
import time
import threading
import logging

from utils.log import setup_logging
from utils.config_loader import load_config
from runners.scenario_runner import run_scenario

SCENARIO_FOLDER = "scenarios"
CONFIG_PATH = "config/config.yaml"

def watch_scenarios(folder_path, callback):
    """
    scenarios/ 폴더를 감시해서 새로운 시나리오 파일이 생기면 실행 콜백 호출
    """
    seen = set(os.listdir(folder_path))
    logging.info(f"시작 시 기존 시나리오 파일 수: {len(seen)}")

    while True:
        try:
            current = set(os.listdir(folder_path))
            new_files = current - seen
            for file in new_files:
                if file.endswith((".yaml", ".yml", ".json", ".csv")):
                    full_path = os.path.join(folder_path, file)
                    logging.info(f"[NEW] 새 시나리오 발견: {file}")
                    callback(full_path)
            seen = current
            time.sleep(2)
        except Exception as e:
            logging.exception("시나리오 감시 중 오류 발생")

def run_scenario_thread(scenario_path, config):
    """
    시나리오를 별도 스레드에서 실행
    """
    try:
        logging.info(f"[RUN] 시나리오 실행 시작: {scenario_path}")
        run_scenario(scenario_path, config)
        logging.info(f"[DONE] 시나리오 종료: {scenario_path}")
    except Exception as e:
        logging.exception(f"[ERROR] 시나리오 실행 중 예외 발생: {scenario_path}")

def main():
    setup_logging()
    logging.info("🔧 이미지 자동화 도구 시작됨")

    config = load_config(CONFIG_PATH)

    def on_new_scenario(path):
        thread = threading.Thread(target=run_scenario_thread, args=(path, config), daemon=True)
        thread.start()

    # 시나리오 감시 스레드 시작
    watcher_thread = threading.Thread(target=watch_scenarios, args=(SCENARIO_FOLDER, on_new_scenario), daemon=True)
    watcher_thread.start()

    try:
        # main thread는 종료되지 않도록 대기
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("사용자에 의해 프로그램이 종료됨 (Ctrl+C)")

if __name__ == "__main__":
    main()