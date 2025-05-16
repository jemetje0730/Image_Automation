import logging
import os
import json
import pyautogui
import cv2
import numpy as np
from action.mouse import click_button
from action.common import wait
from action.keyboard import type_text, press_key, hotkey
from utils.runner_log import get_runner_logger

def run_scenario(scenario_path, config):
    if not os.path.exists(scenario_path):
        logging.error(f"시나리오 파일이 존재하지 않습니다: {scenario_path}")
        return

    runner_logger = get_runner_logger(scenario_path)
    runner_logger.info(f"✅시나리오 시작: {scenario_path}")

    try:
        with open(scenario_path, "r", encoding="utf-8") as f:
            steps = json.load(f)
    except Exception as e:
        runner_logger.error(f"시나리오 파일(JSON) 파싱 실패: {e}")
        return False

    for step in steps:
        if "key" not in step:
            runner_logger.error(f"시나리오 단계에 'key'가 없습니다: {step} - 시나리오 중단")
            return False

        key = step.get("key", "A").strip()
        action = step.get("action", "").strip()
        target = step.get("target", "").strip()
        method = step.get("method", "template").strip()
        position = step.get("position", "center").strip()  # position 기본값 추가

        # duration 처리
        duration = step.get("duration", config.get("delay", 0.5))
        try:
            duration = float(duration)
        except ValueError:
            duration = config.get("delay", 0.5)

        # threshold 처리
        threshold = step.get("threshold", "")
        if threshold == "" or threshold is None:
            threshold = config.get("threshold")
        else:
            try:
                threshold = float(threshold)
            except ValueError:
                threshold = config.get("threshold")

        # min_match_count 처리
        min_match_count = step.get("min_match_count", "")
        if min_match_count == "" or min_match_count is None:
            min_match_count = config.get("min_match_count", 10)
        else:
            try:
                min_match_count = int(min_match_count)
            except ValueError:
                min_match_count = config.get("min_match_count", 10)

        # 결과 비교 처리
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

        # 일반 액션 처리
        image_path = os.path.join(config["image_folder"], target)

        if action in ["click", "double_click", "right_click"]:
            # 로그 메시지 조립
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

            msg += f" | position = {position}"  # position 로그 추가
            runner_logger.info(msg)

            click_args = {
                "image_path": image_path,
                "method": method,
                "threshold": threshold if method == "template" else None,
                "delay": duration,
                "min_match_count": min_match_count if method == "sift" else None,
                "position": position  # click_button에 position 전달
            }

            if action == "double_click":
                click_args["double_click"] = True
            elif action == "right_click":
                click_args["button"] = "right"

            success = click_button(**click_args)
            if not success:
                runner_logger.error(f"❌ {action_map[action]} 실패: {target} - 시나리오 중단")
                return False
            wait(duration)

        elif action == "hotkey":
            keys = target.split("+")
            runner_logger.info(f"[시나리오] 조합 키 입력: {target}")
            hotkey(*keys)
            wait(duration)

        elif action == "type":
            runner_logger.info(f"[시나리오] 텍스트 입력: {target}")
            type_text(target)
            wait(duration)

        elif action == "press":
            runner_logger.info(f"[시나리오] 키 누름: {target}")
            press_key(target)
            wait(duration)

        else:
            runner_logger.warning(f"[시나리오] 알 수 없는 액션: {action}")

    return True
