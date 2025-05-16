import logging
import os

def get_runner_logger(scenario_path: str) -> logging.Logger:
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 파일 이름에서 시나리오 이름만 추출
    scenario_name = os.path.splitext(os.path.basename(scenario_path))[0]
    scenes_log_dir = "logs/scenes"
    os.makedirs(scenes_log_dir, exist_ok=True)

    log_path = os.path.join(scenes_log_dir, f"{scenario_name}.log")

    handler = logging.FileHandler(log_path, encoding="utf-8")  # 회전 없음
    handler.setFormatter(formatter)

    logger = logging.getLogger(f"runner.{scenario_name}")
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        logger.handlers.clear()  # 중복 방지

    logger.addHandler(handler)
    logger.propagate = True  # app.log에도 기록됨

    return logger
