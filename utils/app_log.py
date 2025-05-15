import logging
import os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

def setup_logging(log_dir="logs/app"):
    os.makedirs(log_dir, exist_ok=True)

    today_str = datetime.now().strftime("%Y-%m-%d")
    log_path = os.path.join(log_dir, f"{today_str}.log")

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # 날짜 기반 파일 회전 핸들러
    file_handler = TimedRotatingFileHandler(
        filename=log_path,
        when="midnight",
        interval=1,
        backupCount=20,
        encoding="utf-8",
        utc=False
    )
    file_handler.suffix = "%Y-%m-%d.log"  # 다음날 파일명 형식 설정
    file_handler.setFormatter(formatter)

    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
