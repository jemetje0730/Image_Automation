import logging
import os
import json
import pyautogui
import cv2
import ast
import numpy as np
from action.mouse import click_button
from action.common import wait as wait_for
from action.keyboard import type_text, press_key, hotkey
from db.db_loader import load_scenario_from_db
from utils.runner_log import get_runner_logger

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

        # method 기본값 'template'
        method = (step.get("method") or "template").strip()

        # position 기본값 'center'
        pos_value = step.get("position")
        if pos_value is None:
            position = "center"
        elif isinstance(pos_value, str):
            try:
                # 문자열이 리스트 형태면 실제 리스트로 변환
                position = ast.literal_eval(pos_value)
                if not (isinstance(position, (list, tuple)) and len(position) == 2):
                    position = pos_value.strip()  # 그냥 문자열로 처리
            except:
                position = pos_value.strip()
        else:
            position = pos_value

        # wait 기본값 0.5
        wait_time = step.get("wait")
        if wait_time is None:
            wait_time = 0.5
        else:
            try:
                wait_time = float(wait_time)
            except Exception:
                wait_time = 0.5

        # threshold 기본값 0.85
        threshold = step.get("threshold")
        if threshold is None or threshold == "":
            threshold = 0.85
        else:
            try:
                threshold = float(threshold)
            except Exception:
                threshold = 0.85

        # min_match_count 기본값 10 (sift일 때만)
        min_match_count = step.get("min_match_count")
        if method == "sift":
            if min_match_count is None or min_match_count == "":
                min_match_count = 10
            else:
                try:
                    min_match_count = int(min_match_count)
                except Exception:
                    min_match_count = 10
        else:
            min_match_count = None

        if key == "R" and action == "screen":
            image_path = os.path.join(config["image_folder"], target)
            runner_logger.info(f"[매칭 확인] 화면에서 '{target}' 이미지 찾기")

            if not os.path.exists(image_path):
                runner_logger.error(f"❌ [매칭 실패] 결과 이미지 없음: {image_path}")
                return False

            template = cv2.imread(image_path, cv2.IMREAD_COLOR)
            screenshot = pyautogui.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)

            runner_logger.info(f"[매칭 결과] 매칭 점수: {max_val:.3f} (기준: {threshold})")

            if max_val >= threshold:
                runner_logger.info("🟢 [결과 일치] 다음 단계로 진행")
                continue
            else:
                runner_logger.error("🔴 [결과 불일치] 시나리오 중단")
                return False

        elif key == "R":
            runner_logger.warning(f"[결과 단계 무시] 알 수 없는 R action: {action}")
            continue

        image_path = os.path.join(config["image_folder"], target)

        if action in ["click", "double_click", "right_click"]:
            action_map = {
                "click": "클릭",
                "double_click": "더블 클릭",
                "right_click": "우클릭"
            }
            msg = f"[시나리오] {action_map[action]}: {target} | method = {method}"

            if method == "sift":
                msg += f" | min_match_count = {min_match_count}"
            elif method == "template":
                msg += f" | threshold = {threshold}"

            msg += f" | position = {position}"
            runner_logger.info(msg)

            click_args = {
                "image_path": image_path,
                "method": method,
                "threshold": threshold if method == "template" else None,
                "delay": wait_time,
                "min_match_count": min_match_count if method == "sift" else None,
                "position": position
            }

            if action == "double_click":
                click_args["double_click"] = True
            elif action == "right_click":
                click_args["button"] = "right"

            success = click_button(**click_args)
            if not success:
                runner_logger.error(f"❌ {action_map[action]} 실패: {target} - 시나리오 중단")
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
