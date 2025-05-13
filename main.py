'''
import logging
from utils.log import setup_logging
from utils.config_loader import load_config
from runners.scenario_runner import run_scenario

def main():
    setup_logging()
    config = load_config("config/config.yaml")
    logging.info("자동화 툴 시작")
    run_scenario("scenarios/scenario_1.csv", config)

if __name__ == "__main__":
    main()

'''
# main.py

import logging
from utils.log import setup_logging
from utils.config_loader import load_config

def main():
    setup_logging()  # 로그 설정
    config = load_config("config/config.yaml")  # 설정 파일 로드

    logging.info("✅ main() 함수 시작됨")
    logging.debug(f"불러온 설정: {config}")
    logging.warning("⚠️ 경고 테스트 메시지")
    logging.error("❌ 오류 테스트 메시지")

if __name__ == "__main__":
    main()
