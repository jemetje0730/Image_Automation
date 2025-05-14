import logging
import os

def setup_logging(log_file="logs/scen_tester.log"):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 콘솔 출력
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # 파일 출력
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    # 기본 설정 적용
    logging.basicConfig(
        level=logging.INFO,
        handlers=[console_handler, file_handler]
    )