import pyautogui
import logging

def type_text(text: str, interval: float = 0.05):
    """문자열을 입력합니다 (한 글자씩)."""
    logging.info(f"[KEYBOARD] 입력: '{text}'")
    pyautogui.write(text, interval=interval)

def press_key(key: str):
    """엔터, esc, tab 등 단일 키 입력"""
    logging.info(f"[KEYBOARD] 키 누름: {key}")
    pyautogui.press(key)

def hotkey(*keys: str):
    """복수 키 입력: ctrl+c, shift+tab 등"""
    combo = '+'.join(keys)
    logging.info(f"[KEYBOARD] 조합 키 입력: {combo}")
    pyautogui.hotkey(*keys)
