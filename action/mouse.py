import pyautogui
import time
import logging
from detector.image_detector import find_image_by_template, find_image_by_sift

def click_button(image_path, method="template", threshold=0.85, delay=0.5, double_click=False, button="left", min_match_count=10):
    if method == "template":
        pos = find_image_by_template(image_path, threshold)
    elif method == "sift":
        # min_match_count = min_match_count로 하는 이유는 순서가 다르기 때문
        pos = find_image_by_sift(image_path, min_match_count=min_match_count)
    else:
        logging.error(f"알 수 없는 이미지 탐지 방법: {method}")
        return False

    if pos:
        pyautogui.moveTo(pos[0], pos[1], duration=0.3)
        if double_click:
            pyautogui.click(clicks=2, button=button)
        else:
            pyautogui.click(button=button)
        logging.info(f"{method} 방식으로 {button} 버튼 {'더블클릭' if double_click else '클릭'} 완료: {image_path}")
        time.sleep(delay)
        return True
    else:
        logging.error(f"{method} 방식으로 이미지 클릭 실패: {image_path}")
        return False
