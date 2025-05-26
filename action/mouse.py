import pyautogui
import time
import logging
from detector.image_detector import find_image_by_template, find_image_by_sift

def click_button(image_path, threshold=0.85, sift_threshold=0.7, min_match_count=10, delay=0.5,
                 double_click=False, button="left", position="center"):
    used_method = None
    pos, size = find_image_by_template(image_path, threshold=threshold, return_size=True)
    if pos is not None:
        used_method = "TEMPLATE"
    else:
        pos, size = find_image_by_sift(image_path, sift_threshold=sift_threshold, min_match_count=min_match_count, return_size=True)
        if pos is not None:
            used_method = "SIFT"

    if pos:
        center_x, center_y = pos
        w, h = size

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

        logging.info(f"이미지 클릭 완료: {image_path} | 방식: {used_method}")
        time.sleep(delay)
        return True
    else:
        logging.error(f"이미지 클릭 실패: {image_path}")
        return False

