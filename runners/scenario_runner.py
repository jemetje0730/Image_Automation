import logging
import os
import json
import pyautogui
import cv2
import numpy as np
from action.mouse import click_button, double_click_button
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
            return False # 키 없으면 중단
        
        key = step.get("key", "A").strip()
        action = step.get("action", "").strip()
        target = step.get("target", "").strip()
        duration = step.get("duration", config.get("delay", 0.5))
        threshold = step.get("threshold", "") # threshold 값 읽기 (없으면 빈 문자열)

        try:
            duration = float(duration)
        except ValueError:
            duration = config.get("delay", 0.5)
        
        # threshold 값 처리: 빈 문자열이면 config 기본값, 아니면 float 변환
        if threshold == "" or threshold is None:
            threshold = config.get("threshold")
        else:
            try:
                threshold = float(threshold)
            except ValueError:
                threshold = config.get("threshold")

        # 결과 비교 먼저 처리
        if key == "R":
            if action == "screen":
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

                threshold = config.get("threshold")
                runner_logger.info(f"[매칭 결과] 매칭 점수: {max_val:.3f} (기준: {threshold})")

                if max_val >= threshold:
                    runner_logger.info("🟢 [결과 일치] 다음 단계로 진행")
                    continue
                else:
                    runner_logger.error("🔴 [결과 불일치] 시나리오 중단")
                    return False
            else:
                runner_logger.warning(f"[결과 단계 무시] 알 수 없는 R action: {action}")
                continue  # 알 수 없는 R 액션 무시

        # 일반 액션 처리 (key == "A")
        if action == "click":
            image_path = os.path.join(config["image_folder"], target)
            runner_logger.info(f"[시나리오] 클릭: {target}| threshold = {threshold}")
            click_button(image_path, threshold=config.get("threshold", 0.85), delay=duration)
            wait(duration)

        elif action == "double_click":
            image_path = os.path.join(config["image_folder"], target)
            runner_logger.info(f"[시나리오] 더블 클릭: {target}")
            double_click_button(image_path, threshold=config.get("threshold", 0.85), delay=duration)
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