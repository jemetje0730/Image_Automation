# runners/scenario_runner.py
import csv
import logging
from detector.image_detector import find_image
from action.mouse import click_image
import time

def run_scenario(scenario_path, config):
    with open(scenario_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for step in reader:
            action = step["action"]
            target = step["target"]
            duration = float(step.get("duration", 0))

            if action == "click":
                img_path = f"{config['image_folder']}/{target}"
                location = find_image(img_path, config["threshold"])
                if location:
                    click_image(location)
                    logging.info(f"클릭 성공: {target}")
                else:
                    logging.warning(f"이미지를 찾을 수 없음: {target}")
            elif action == "wait":
                logging.info(f"{duration}초 대기")
                time.sleep(duration)
