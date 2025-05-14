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
