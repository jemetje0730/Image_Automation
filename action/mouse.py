import pyautogui
import time
import logging
from detector.image_detector import detect_image

def click_button(image_path, threshold, sift_threshold, min_match_count, min_match_ratio, delay,
                 double_click=False, button="left", position="center", info_score_threshold=None):

    if info_score_threshold is None:
        logging.error("info_score_threshold 값이 제공되지 않았습니다.")
        return False

    config = {
        "threshold": threshold,
        "sift_threshold": sift_threshold,
        "min_match_count": min_match_count,
        "info_score_threshold": info_score_threshold,
        "min_match_ratio": min_match_ratio
    }

    pos, size = detect_image(
        image_path,
        config=config,
        return_size=True
    )

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

        logging.info(f"[MOUSE] 이미지 클릭 완료: {image_path}")
        time.sleep(delay)
        return True
    else:
        logging.error(f"[MOUSE] 이미지 클릭 실패: {image_path}")
        return False
