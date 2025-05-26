import logging
import os
import json
import ast
from action.mouse import click_button
from action.common import wait as wait_for
from action.keyboard import type_text, press_key, hotkey
from db.db_loader import load_scenario_from_db
from utils.runner_log import get_runner_logger
from detector.image_detector import find_image_by_template, find_image_by_sift

def run_scenario(scenario_path_or_id, config, input_type='json'):
    steps = []

    try:
        if input_type == "json":
            if not os.path.exists(scenario_path_or_id):
                logging.error(f"시나리오 파일이 존재하지 않습니다: {scenario_path_or_id}")
                return False

            runner_logger = get_runner_logger(scenario_path_or_id)
            runner_logger.info(f"✅시나리오 시작: {scenario_path_or_id} (type={input_type})")

            with open(scenario_path_or_id, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, dict) and "baseAction" in data and "scenario" in data:
                base_action = data["baseAction"]
                for step in data["scenario"]:
                    merged = base_action.copy()
                    merged.update(step)
                    steps.append(merged)
            else:
                steps = data

        elif input_type == "db":
            scenario_name = f"db_log:base_id={scenario_path_or_id}"
            runner_logger = get_runner_logger(scenario_name)
            runner_logger.info(f"✅ DB 시나리오 실행 시작: base_id={scenario_path_or_id}")

            steps = load_scenario_from_db(config.get("db_path", "scenario.db"), base_id=int(scenario_path_or_id))

        else:
            logging.error(f"지원하지 않는 시나리오 타입: {input_type}")
            return False

    except Exception as e:
        logging.error(f"시나리오 로딩 중 예외 발생: {e}")
        return False

    for step in steps:
        if "key" not in step:
            runner_logger.error(f"시나리오 단계에 'key'가 없습니다: {step} - 시나리오 중단")
            return False

        key = step.get("key", "A").strip()
        action = step.get("action", "").strip()
        target = step.get("target", "").strip()

        pos_value = step.get("position")
        if pos_value is None:
            position = "center"
        elif isinstance(pos_value, str):
            try:
                position = ast.literal_eval(pos_value)
                if not (isinstance(position, (list, tuple)) and len(position) == 2):
                    position = pos_value.strip()
            except:
                position = pos_value.strip()
        else:
            position = pos_value

        wait_time = step.get("wait")
        if wait_time is None:
            wait_time = 0.5
        else:
            try:
                wait_time = float(wait_time)
            except Exception:
                wait_time = 0.5

        threshold = step.get("threshold")
        if threshold is None or threshold == "":
            threshold = float(config.get("threshold", 0.85))
        else:
            try:
                threshold = float(threshold)
            except Exception:
                threshold = float(config.get("threshold", 0.85))

        sift_threshold = step.get("sift_threshold")
        if sift_threshold is None or sift_threshold == "":
            sift_threshold = float(config.get("sift_threshold", threshold))
        else:
            try:
                sift_threshold = float(sift_threshold)
            except Exception:
                sift_threshold = float(config.get("sift_threshold", threshold))

        image_path = os.path.join(config["image_folder"], target)

        if key == "R" and action == "screen":
            runner_logger.info(f"[매칭 확인] 화면에서 '{target}' 이미지 찾기")

            if not os.path.exists(image_path):
                runner_logger.error(f"❌ [매칭 실패] 결과 이미지 없음: {image_path}")
                return False

            found = find_image_by_template(image_path, threshold=threshold)
            if found is None:
                found = find_image_by_sift(image_path, sift_threshold=sift_threshold)

            if found is not None:
                runner_logger.info(f"🟢 [이미지 매칭 성공] 다음 단계로 진행")
                continue
            else:
                runner_logger.error("🔴 [모든 이미지 매칭 실패] 시나리오 중단")
                return False

        if action in ["click", "double_click", "right_click"]:
            runner_logger.info(f"[시나리오] 클릭 관련 작업 수행: {target}")

            click_args = {
                "image_path": image_path,
                "threshold": threshold,
                "sift_threshold": sift_threshold,
                "delay": wait_time,
                "position": position,
                "button": "right" if action == "right_click" else "left",
                "double_click": action == "double_click"
            }

            success = click_button(**click_args)
            if not success:
                runner_logger.error(f"❌ 클릭 실패: {target} - 시나리오 중단")
                return False

            wait_for(wait_time)

        elif action == "hotkey":
            keys = target.split("+")
            runner_logger.info(f"[시나리오] 조합 키 입력: {target}")
            hotkey(*keys)
            wait_for(wait_time)

        elif action == "type":
            runner_logger.info(f"[시나리오] 텍스트 입력: {target}")
            type_text(target)
            wait_for(wait_time)

        elif action == "press":
            runner_logger.info(f"[시나리오] 키 누름: {target}")
            press_key(target)
            wait_for(wait_time)

        else:
            runner_logger.warning(f"[시나리오] 알 수 없는 액션: {action}")

    return True
