import pyautogui
import cv2
import numpy as np
from collections import deque
import logging
import os

prev_success_scale = 1.0  # 이전 성공 스케일 기억용

def find_image_by_template(image_path, threshold=0.85, return_size=False):
    global prev_success_scale

    if not os.path.exists(image_path):
        logging.error(f"이미지 파일이 존재하지 않음: {image_path}")
        return (None, None) if return_size else None

    template = cv2.imread(image_path, cv2.IMREAD_COLOR)
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    all_scales = np.linspace(0.5, 3.0, 15)
    scale_queue = deque([prev_success_scale] + [s for s in all_scales if abs(s - prev_success_scale) > 1e-6])

    best_match = -1.0
    while scale_queue:
        scale = scale_queue.popleft()

        resized = cv2.resize(template, None, fx=scale, fy=scale)
        h, w = resized.shape[:2]

        result = cv2.matchTemplate(screenshot, resized, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val > best_match:
            best_match = max_val

        if max_val >= threshold:
            center = (max_loc[0] + w // 2, max_loc[1] + h // 2)
            prev_success_scale = scale
            logging.info(f"'{image_path}' 매칭 성공 | 점수: {max_val:.3f}, 스케일: {scale:.2f}")
            return (center, (w, h)) if return_size else center

    logging.warning(f"'{image_path}' 탐지 실패 | 최고 점수: {best_match:.3f}")
    return (None, None) if return_size else None

def find_image_by_sift(image_path, sift_threshold=0.85, min_match_count=10, return_size=False):
    if not os.path.exists(image_path):
        logging.error(f"[SIFT] 이미지 파일 없음: {image_path}")
        return (None, None) if return_size else None

    template = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    screenshot = pyautogui.screenshot()
    screen_gray = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

    sift = cv2.SIFT_create()

    kp1, des1 = sift.detectAndCompute(template, None)
    kp2, des2 = sift.detectAndCompute(screen_gray, None)

    if des1 is None or des2 is None:
        logging.warning(f"[SIFT] 키포인트 부족")
        return (None, None) if return_size else None

    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)

    good_matches = []
    for m, n in matches:
        if m.distance < sift_threshold * n.distance:
            good_matches.append(m)

    if len(good_matches) < min_match_count:
        logging.info(f"[SIFT] 매칭 실패 - 매치 수: {len(good_matches)} (최소 필요: {min_match_count})")
        return (None, None) if return_size else None

    match_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches])
    median_x = int(np.median(match_pts[:, 0]))
    median_y = int(np.median(match_pts[:, 1]))

    h, w = template.shape[:2]
    logging.info(f"[SIFT] '{image_path}' 매칭 성공 | 매치 수: {len(good_matches)}")
    return ((median_x, median_y), (w, h)) if return_size else (median_x, median_y)
