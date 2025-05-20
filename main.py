import logging
from utils.app_log import setup_logging
from utils.config_loader import load_config
from runners.scenario_runner import run_scenario
from utils.log_clean import manage_log_files

def main():
    setup_logging()
    manage_log_files()
    config = load_config("config/config.yaml")
    logging.info("자동화 툴 시작")

    if not run_scenario("scenarios/scenario_1.json", config):
        logging.error("❌ scenario_1 실패: 자동화를 중단합니다.")
        return
    
    if not run_scenario(1, config, input_type="db"):
        logging.error("❌ DB 시나리오 실패: 자동화를 중단합니다.")
        return

    json_path = "scenarios/scenario_2.json"
    if not run_scenario(json_path, config, input_type="json"):
        logging.error("❌ scenario_2 실패: 자동화를 중단합니다.")
        return

    logging.info("🎉 모든 시나리오 실행 완료")
    
if __name__ == "__main__":
    main()