import csv
import logging
import time
import os
from action.mouse import click_button

def run_scenario(scenario_path, config):
    if not os.path.exists(scenario_path):
        logging.error(f"시나리오 파일을 찾을 수 없습니다: {scenario_path}")
        return

    with open(scenario_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for step in reader:
            action = step.get("action", "").strip()
            target = step.get("target", "").strip()
            duration = float(step.get("duration", config.get("delay", 0.5)))

            if action == "click":
                image_path = os.path.join(config["image_folder"], target)
                logging.info(f"[시나리오] 클릭 시도: {target}")
                click_button(image_path, threshold=config.get("threshold", 0.85), delay=duration)

            elif action == "wait":
                logging.info(f"[시나리오] 대기: {duration:.1f}초")
                time.sleep(duration)

            else:
                logging.warning(f"[시나리오] 알 수 없는 액션: {action}")
