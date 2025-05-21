# utils/rename_scenario.py
import os
import re
from runners.scenario_runner import run_scenario
import logging

def rename_scenarios(scenario_dir="scenarios"):
    """
    scenarios 디렉토리 내 json 파일을 생성시간 순서로 정렬하고
    파일 이름 앞에 1_, 2_, ... 순서를 붙임
    """
    files = [
        f for f in os.listdir(scenario_dir) if f.endswith(".json")
    ]

    file_info = []
    for f in files:
        full_path = os.path.join(scenario_dir, f)
        created_time = os.path.getctime(full_path)
        parts = f.split("_", 1)
        base_name = parts[1] if parts[0].isdigit() and len(parts) > 1 else f
        file_info.append((base_name, created_time, full_path))

    # 생성 시간 기준 정렬
    file_info.sort(key=lambda x: x[1])

    for idx, (base_name, _, old_path) in enumerate(file_info, start=1):
        new_name = f"{idx}_{base_name}"
        new_path = os.path.join(scenario_dir, new_name)
        if os.path.basename(old_path) != new_name:
            os.rename(old_path, new_path)
            print(f" 리네이밍: {os.path.basename(old_path)} → {new_name}")

def run_json_scenarios(config, scenario_dir="scenarios"):
    """
    JSON 파일을 번호 순서대로 실행하며, 실패 시 중단
    """
    def extract_number(filename):
        match = re.match(r'^(\d+)', filename)
        return int(match.group(1)) if match else float('inf')

    scenario_files = sorted(
        [f for f in os.listdir(scenario_dir) if f.endswith(".json")],
        key=extract_number
    )

    for scenario_file in scenario_files:
        full_path = os.path.join(scenario_dir, scenario_file)
        success = run_scenario(full_path, config)
        if not success:
            logging.error(f"❌ {scenario_file} 실패: 자동화를 중단합니다.")
            return False
    return True
