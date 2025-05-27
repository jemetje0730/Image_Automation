import pyautogui
import cv2
import numpy as np
from collections import deque, Counter
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
            logging.info(f"[MATCH] '{image_path}' 매칭 성공 | 점수: {max_val:.3f}, 스케일: {scale:.2f}")
            return (center, (w, h)) if return_size else center

    logging.warning(f"'{image_path}' 탐지 실패 | 최고 점수: {best_match:.3f}")
    return (None, None) if return_size else None

def find_image_by_sift(image_path, sift_threshold=0.7, min_match_ratio=0.1, min_match_count=None, return_size=False):
    if not os.path.exists(image_path):
        logging.error(f"[SIFT] 이미지 파일 없음: {image_path}")
        return (None, None) if return_size else None

    template = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    screenshot = pyautogui.screenshot()
    screen_gray = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

    sift = cv2.SIFT_create()
    kp1, des1 = sift.detectAndCompute(template, None)
    kp2, des2 = sift.detectAndCompute(screen_gray, None)

    total_kp = len(kp1)

    # 키포인트가 5개 미만이면 템플릿 매칭으로 전환
    if des1 is None or des2 is None or total_kp < 5:
        logging.warning(f"[SIFT] 전체 키포인트 부족 → Template Matching 사용")
        return find_image_by_template(image_path, threshold=0.85, return_size=return_size)

    # 최소 매칭 기준 설정
    if min_match_count is None:
        calc_count = int(total_kp * min_match_ratio)
        # 5 이상, total_kp 이하로 보정
        min_match_count = min(max(calc_count, 5), total_kp)

    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)
    good_matches = [m for m, n in matches if m.distance < sift_threshold * n.distance]

    logging.info(f"[SIFT] 최소 매칭 기준: {min_match_count}개 (전체 키포인트: {total_kp}), 현재 매칭 개수: {len(good_matches)}개")

    if total_kp < min_match_count:
        logging.warning(f"[SIFT] 전체 키포인트({total_kp})가 최소 매칭 기준({min_match_count})보다 적어 Template Matching으로 전환")
        return find_image_by_template(image_path, threshold=0.8, return_size=return_size)

    if len(good_matches) < min_match_count:
        logging.info(f"[SIFT] 매칭 실패 - 매치 수: {len(good_matches)} (최소 필요: {min_match_count})")
        return (None, None) if return_size else None

    src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    if M is None:
        logging.warning("[SIFT] Homography 계산 실패")
        return (None, None) if return_size else None

    h, w = template.shape[:2]
    corners = np.float32([[0, 0], [w, 0], [w, h], [0, h]]).reshape(-1, 1, 2)
    transformed_corners = cv2.perspectiveTransform(corners, M)

    top_left = transformed_corners[0][0]  # 좌상단
    center_x = int(top_left[0] + w / 2)
    center_y = int(top_left[1] + h / 2)

    if return_size:
        return (center_x, center_y), (w, h)
    else:
        return (center_x, center_y)

def detect_image(image_path, config, return_size=False):
    def evaluate_image_info_score(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size

        contrast = np.std(gray)

        sift = cv2.SIFT_create()
        kp, _ = sift.detectAndCompute(gray, None)
        kp_count = len(kp)

        small = cv2.resize(img, (64, 64))
        pixels = small.reshape(-1, 3)
        most_common = Counter(map(tuple, pixels)).most_common(1)[0][1] / len(pixels)

        score = (
            (1 - most_common) * 0.3 +
            min(edge_density * 3, 1) * 0.3 +
            min(kp_count / 100, 1) * 0.2 +
            min(contrast / 100, 1) * 0.2
        )
        return score

    if not os.path.exists(image_path):
        logging.error(f"이미지 없음: {image_path}")
        if return_size:
            return None, None
        else:
            return None

    template = cv2.imread(image_path)
    info_score = evaluate_image_info_score(template)
    logging.info(f"[INFO SCORE] {image_path} = {info_score:.2f}")

    info_score_threshold = config["info_score_threshold"]
    
    if info_score >= info_score_threshold:
        logging.info("[IMAGE] 정보 충분 → SIFT 시도")
        return find_image_by_sift(
            image_path,
            sift_threshold=config["sift_threshold"],
            min_match_ratio=config["min_match_ratio"],
            min_match_count=config["min_match_count"],
            return_size=return_size
        )
    else:
        logging.info("[IMAGE] 정보 부족 → Template 시도")
        return find_image_by_template(
            image_path,
            threshold=config["threshold"],
            return_size=return_size
        )