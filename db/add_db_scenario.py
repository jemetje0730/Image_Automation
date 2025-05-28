from db_loader import add_scenario_to_db

# 기존 JSON 기반 시나리오 정의
data = {
  "scenario": [
    {"target": "lidar.png"},
    {"target": "channel.png", "position": [0.85, 0.5]},
    {"target": "confirm.png", "position": [0.85, 0.5]},
    {"target": "detect.png", "wait": 0, "position": [0.85, 0.75]},
    {"target": "detect.png", "wait": 0, "position": [0.85, 0.75]},
    {"target": "detect.png", "wait": 0, "position": [0.85, 0.75]},
    {"target": "confirm2.png", "wait": 1, "position": [0.90, 0.85]},
    {"target": "confirm3.png", "wait": 0.5, "position": [0.95, 0.85]},
    {"target": "exit.png", "position": "right"},
    {"key": "R", "action": "screen", "target": "result2.png", "wait": 0.5},
    # step 추가
    {"target": "search.png"},
    {"action": "type", "target": "microsoft edge"},
    {"action": "press", "target": "enter"},
    {"action": "type", "target": "gp"},
    {"action": "press", "target": "enter", "wait": 5},
    {"target": "out.png", "wait": 3},
    {"target": "out.png"}
    ]
}

def pos_to_str(pos):
    if isinstance(pos, list):
        return ",".join(map(str, pos))
    return pos

def add_scenario():
    steps = []
    for step in data["scenario"]:
        steps.append({
            "key": step.get("key", "A"), # 기본 key는 "A"
            "action": step.get("action", None),
            "target": step["target"],
            "position": pos_to_str(step.get("position")),
            "wait": step.get("wait", 0.5),
            "threshold": None,
            "min_match_count": None,
            "method": None
        })

    add_scenario_to_db(
        db_path="scenarios/scenario.db",
        base_id=1,  # base_id는 db_setup.py에서 설정한 ID
        steps=steps
    )
    print("✅ DB에 시나리오 steps 삽입 완료")

if __name__ == "__main__":
    add_scenario()
