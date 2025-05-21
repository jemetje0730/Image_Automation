# main.py
import logging
from utils.app_log import setup_logging
from utils.config_loader import load_config
from utils.log_clean import manage_log_files
from utils.arrange_scenario import rename_scenarios, run_json_scenarios
from runners.scenario_runner import run_scenario

def main():
    setup_logging()
    manage_log_files()
    config = load_config("config/config.yaml")
    logging.info("자동화 툴 시작")
    rename_scenarios()

    # JSON 시나리오 실행
    if not run_json_scenarios(config):
        return

    # DB 시나리오 실행
    if not run_scenario(1, config, input_type="db"):
        logging.error("❌ DB 시나리오 실패: 자동화를 중단합니다.")
        return

    logging.info("🎉 모든 시나리오 실행 완료")

if __name__ == "__main__":
    main()
