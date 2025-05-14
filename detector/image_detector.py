import pyautogui
import cv2
import numpy as np
from collections import deque
import logging
import os

prev_success_scale = 1.0
match_debug = 0

def find_image_on_screen(image_path, threshold=0.85, debug=False, debug_dir="logs/debug"):
    global prev_success_scale, match_debug

    if not os.path.exists(image_path):
        logging.error(f"이미지 파일이 존재하지 않음: {image_path}")
        return None

    template = cv2.imread(image_path, cv2.IMREAD_COLOR)
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    all_scales = np.linspace(0.5, 3.0, 15)
    scale_queue = deque([prev_success_scale] + [s for s in all_scales if abs(s - prev_success_scale) > 1e-6])

    best_match = -1.0
    for scale in scale_queue:
        resized = cv2.resize(template, None, fx=scale, fy=scale)
        h, w = resized.shape[:2]

        result = cv2.matchTemplate(screenshot, resized, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val > best_match:
            best_match = max_val

        if max_val >= threshold:
            center = (max_loc[0] + w // 2, max_loc[1] + h // 2)

            if debug:
                os.makedirs(debug_dir, exist_ok=True)
                debug_img = screenshot.copy()
                cv2.rectangle(debug_img, max_loc, (max_loc[0]+w, max_loc[1]+h), (0, 255, 0), 2)
                match_debug_path = os.path.join(debug_dir, f"match_{match_debug}.png")
                cv2.imwrite(match_debug_path, debug_img)

            prev_success_scale = scale
            logging.info(f"✅ '{image_path}' 매칭 성공 | 점수: {max_val:.3f}, 스케일: {scale:.2f}")
            return center

    logging.warning(f"❌ '{image_path}' 탐지 실패 | 최고 점수: {best_match:.3f}")
    return None
