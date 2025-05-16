import pyautogui
import time
import logging
from detector.image_detector import find_image_by_template, find_image_by_sift

def click_button(image_path, method="template", threshold=0.85, delay=0.5,
                 double_click=False, button="left", min_match_count=10, position="center"):
    if method == "template":
        pos, size = find_image_by_template(image_path, threshold, return_size=True)
    elif method == "sift":
        pos, size = find_image_by_sift(image_path, min_match_count=min_match_count, return_size=True)
    else:
        logging.error(f"알 수 없는 이미지 탐지 방법: {method}")
        return False

    if pos:
        x, y = pos
        w, h = size
        offset = 15  # 클릭 위치 안전 여유

        position_map = {
            "center": (x, y),
            "top_left": (x - w // 2 + offset, y - h // 2 + offset),
            "top_right": (x + w // 2 - offset, y - h // 2 + offset),
            "bottom_left": (x - w // 2 + offset, y + h // 2 - offset),
            "bottom_right": (x + w // 2 - offset, y + h // 2 - offset),
            "top": (x, y - h // 2 + offset),
            "bottom": (x, y + h // 2 - offset),
            "left": (x - w // 2 + offset, y),
            "right": (x + w // 2 - offset, y),
        }

        click_x, click_y = position_map.get(position, (x, y))

        pyautogui.moveTo(click_x, click_y, duration=0.3)
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
