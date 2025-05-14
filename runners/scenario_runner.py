import csv
import logging
import os
from action.mouse import click_button
from action.common import wait  # ✅ 추가됨

def run_scenario(scenario_path, config):
    if not os.path.exists(scenario_path):
        logging.error(f"시나리오 파일이 존재하지 않습니다: {scenario_path}")
        return

    with open(scenario_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for step in reader:
            action = step.get("action", "").strip()
            target = step.get("target", "").strip()
            # csv에 duration이 없을 경우 config에서 기본 값 0.5초를 사용
            duration_str = step.get("duration", "").strip()
            duration = float(duration_str) if duration_str else config.get("delay", 0.5)

            if action == "click":
                image_path = os.path.join(config["image_folder"], target)
                logging.info(f"[시나리오] 클릭 시도: {target}")
                click_button(image_path, threshold=config.get("threshold", 0.85), delay=duration)

            elif action == "wait":
                wait(duration)  # ✅ 변경된 부분

            else:
                logging.warning(f"[시나리오] 알 수 없는 액션: {action}")
