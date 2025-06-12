import logging
import os
import json
import ast
from action.mouse import click_button
from action.common import wait as wait_for
from action.keyboard import type_text, press_key, hotkey
from db.db_loader import load_scenario_from_db
from utils.runner_log import get_runner_logger
from detector.image_detector import detect_image  

def run_scenario(scenario_path_or_id, config, input_type='json'):
    steps = []

    try:
        if input_type == "json":
            if not os.path.exists(scenario_path_or_id):
                logging.error(f"시나리오 파일이 존재하지 않습니다: {scenario_path_or_id}")
                return False

            runner_logger = get_runner_logger(scenario_path_or_id)
            runner_logger.info(f"✅ 시나리오 시작: {scenario_path_or_id} (type={input_type})")

            with open(scenario_path_or_id, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, dict) and "baseAction" in data and "scenario" in data:
                base_action = data["baseAction"]
                for step in data["scenario"]:
                    merged = base_action.copy()
                    merged.update(step)
                    steps.append(merged)
            else:
                steps = data

        elif input_type == "db":
            scenario_name = f"db_log:base_id={scenario_path_or_id}"
            runner_logger = get_runner_logger(scenario_name)
            runner_logger.info(f"✅ DB 시나리오 실행 시작: base_id={scenario_path_or_id}")

            steps = load_scenario_from_db(config["db_path"], base_id=int(scenario_path_or_id))

        else:
            logging.error(f"지원하지 않는 시나리오 타입: {input_type}")
            return False

    except Exception as e:
        logging.error(f"시나리오 로딩 중 예외 발생: {e}")
        return False

    for step in steps:
        if "key" not in step:
            runner_logger.error(f"시나리오 단계에 'key'가 없습니다: {step} - 시나리오 중단")
            return False

        key = step.get("key", "A").strip()
        action = step.get("action", "").strip()
        target = step.get("target", "").strip()

        # Position 처리
        pos_value = step.get("position")
        if pos_value is None:
            position = "center"
        elif isinstance(pos_value, str):
            try:
                position = ast.literal_eval(pos_value)
                if not (isinstance(position, (list, tuple)) and len(position) == 2):
                    position = pos_value.strip()
            except:
                position = pos_value.strip()
        else:
            position = pos_value

        # 대기시간
        try:
            wait_time = float(step.get("wait", config["delay"]))
        except:
            wait_time = config["delay"]

        # threshold 설정
        threshold = float(step.get("threshold") or config["threshold"])
        sift_threshold = float(step.get("sift_threshold") or config["sift_threshold"])
        min_match_ratio = float(step.get("min_match_ratio") or config["min_match_ratio"])
        info_score_threshold = float(step.get("info_score_threshold") or config["info_score_threshold"])
        
        raw_min_match_count = step.get("min_match_count")
        if raw_min_match_count is None:
            raw_min_match_count = config.get("min_match_count")

        if raw_min_match_count is None:
            min_match_count = None
        else:
            min_match_count = int(raw_min_match_count)


        # 이미지가 필요한 경우만 image_path 설정
        if action in ["click", "double_click", "right_click", "screen"]:
            image_path = os.path.join(config["image_folder"], target)

            if not os.path.exists(image_path):
                runner_logger.error(f"❌ 이미지 파일이 없음: {image_path}")
                return False
        else:
            image_path = None

        # 화면에서 이미지 찾기 (자동 SIFT/TEMPLATE)
        if key == "R" and action == "screen":
            runner_logger.info(f"[매칭 확인] 화면에서 '{target}' 이미지 찾기")

            # config 복사
            step_config = config.copy()
            step_config["threshold"] = threshold
            step_config["sift_threshold"] = sift_threshold
            step_config["min_match_count"] = min_match_count
            step_config["info_score_threshold"] = info_score_threshold
            step_config["min_match_ratio"] = min_match_ratio

            found = detect_image(image_path, step_config)

            if found is not None:
                runner_logger.info(f"🟢 [이미지 매칭 성공] 다음 단계로 진행")
                continue
            else:
                runner_logger.error("🔴 [모든 이미지 매칭 실패] 시나리오 중단")
                return False

        # 클릭 액션 처리
        if action in ["click", "double_click", "right_click"]:
            runner_logger.info(f"[SCENARIO] 클릭 관련 작업 수행: {target}")

            click_args = {
                "image_path": image_path,
                "threshold": threshold,
                "sift_threshold": sift_threshold,
                "min_match_count": min_match_count,
                "min_match_ratio": min_match_ratio,
                "delay": wait_time,
                "position": position,
                "button": "right" if action == "right_click" else "left",
                "double_click": action == "double_click",
                "info_score_threshold": info_score_threshold
            }

            success = click_button(**click_args)
            if not success:
                runner_logger.error(f"❌ 클릭 실패: {target} - 시나리오 중단")
                return False

            wait_for(wait_time)

        elif action == "hotkey":
            keys = target.split("+")
            runner_logger.info(f"[SCENARIO] 조합 키 입력: {target}")
            hotkey(*keys)
            wait_for(wait_time)

        elif action == "type":
            runner_logger.info(f"[SCENARIO] 텍스트 입력: {target}")
            type_text(target)
            wait_for(wait_time)

        elif action == "press":
            runner_logger.info(f"[SCENARIO] 키 누름: {target}")
            press_key(target)
            wait_for(wait_time)

        else:
            runner_logger.warning(f"[SCENARIO] 알 수 없는 액션: {action}")

    return True

def run_all_db_scenarios(config):
    db_folder = config.get("db_folder", "scenarios")

    for filename in os.listdir(db_folder):
        if not filename.endswith(".db"):
            continue

        db_path = os.path.join(db_folder, filename)
        logging.info(f" DB 파일 실행 시작: {db_path}")

        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()

            cur.execute("SELECT DISTINCT base_id FROM baseAction ORDER BY base_id")
            base_ids = [row[0] for row in cur.fetchall()]
            conn.close()

            if not base_ids:
                logging.warning(f"⚠ base_id 없음: {db_path}")
                continue

            for base_id in base_ids:
                logging.info(f"실행 시작 from {filename}")
                local_config = config.copy()
                local_config["db_path"] = db_path

                success = run_scenario(base_id, local_config, input_type="db")
                if not success:
                    logging.error(f"❌ base_id={base_id} 실패 (파일: {filename}) - 다음 base_id로 진행")
                    continue

        except Exception as e:
            logging.error(f"❌ DB 순회 중 오류: {db_path} - {e}")
            continue
