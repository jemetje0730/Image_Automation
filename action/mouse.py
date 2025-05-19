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
        center_x, center_y = pos
        w, h = size

        # 문자열 position을 비율로 매핑
        position_map = {
            "center": (0.5, 0.5),
            "top_left": (0.0, 0.0),
            "top_right": (1.0, 0.0),
            "bottom_left": (0.0, 1.0),
            "bottom_right": (1.0, 1.0),
            "top": (0.5, 0.0),
            "bottom": (0.5, 1.0),
            "left": (0.0, 0.5),
            "right": (1.0, 0.5),
        }

        if isinstance(position, str):
            x_ratio, y_ratio = position_map.get(position, (0.5, 0.5))
        elif isinstance(position, (tuple, list)) and len(position) == 2:
            x_ratio, y_ratio = position
        else:
            logging.error(f"잘못된 position 값: {position}")
            return False

        click_x = int(center_x + (x_ratio - 0.5) * w)
        click_y = int(center_y + (y_ratio - 0.5) * h)


        pyautogui.moveTo(click_x, click_y, duration=0.3)
        pyautogui.click(button=button, clicks=2 if double_click else 1)

        logging.info(f"{method} 방식으로 {button} 버튼 {'더블클릭' if double_click else '클릭'} 완료: {image_path}")
        time.sleep(delay)
        return True
    else:
        logging.error(f"{method} 방식으로 이미지 클릭 실패: {image_path}")
        return False
