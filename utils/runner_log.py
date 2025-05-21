import logging
import os

def get_runner_logger(scenario_path: str) -> logging.Logger:
    """
    시나리오 실행 전용 로거 생성:
    - JSON 파일일 경우: 파일명 기반 로그 생성 (e.g., scenario_1.json → scenario_1.log)
    - DB 기반 실행일 경우: scenario_db.log
    """
    # 로그 포맷 정의
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 로그 디렉토리 생성
    scenes_log_dir = "logs/scenes"
    os.makedirs(scenes_log_dir, exist_ok=True)

    # 시나리오 이름 추출
    if scenario_path.isdigit() or scenario_path.startswith("db_log:"):
        scenario_name = "scenario_db"
    else:
        scenario_name = os.path.splitext(os.path.basename(scenario_path))[0]

    log_path = os.path.join(scenes_log_dir, f"{scenario_name}.log")

    # 중복 로거 방지 (이름 기준으로 생성)
    logger = logging.getLogger(f"runner.{scenario_name}")
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        logger.handlers.clear()

    # 파일 핸들러 추가
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.propagate = True  # 상위 로거(app.log 등)에 전달 허용

    return logger
