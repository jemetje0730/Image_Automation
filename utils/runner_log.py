import logging
import os

def get_runner_logger(scenario_path: str) -> logging.Logger:
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    scenes_log_dir = "logs/scenes"
    os.makedirs(scenes_log_dir, exist_ok=True)

    # ✅ DB 시나리오 감지 (숫자 or "db_log:" 접두사 등)
    if scenario_path.isdigit() or scenario_path.startswith("db_log:"):
        scenario_name = "scenario_db"
    else:
        scenario_name = os.path.splitext(os.path.basename(scenario_path))[0]

    log_path = os.path.join(scenes_log_dir, f"{scenario_name}.log")

    logger = logging.getLogger(f"runner.{scenario_name}")
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        logger.handlers.clear()

    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.propagate = True  # app.log에도 기록됨

    return logger
