import pyautogui
import time
import logging
from detector.image_detector import find_image_on_screen

def click_button(image_path, threshold=0.85, delay=0.5, debug=False):
    pos = find_image_on_screen(image_path, threshold, debug=debug)
    if pos:
        pyautogui.moveTo(pos[0], pos[1], duration=0.3)
        pyautogui.doubleClick()
        logging.info(f"🖱️ 클릭 완료: {image_path}")
        time.sleep(delay)
    else:
        logging.error(f"🛑 이미지 클릭 실패: {image_path}")
