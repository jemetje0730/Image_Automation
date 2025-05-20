from db_loader import add_scenario_to_db

data = {
  "baseAction": {
    "key": "A",
    "action": "click",
    "wait": 0.5
  },
  "scenario": [
    {"target": "lidar.png"},
    {"target": "channel.png", "position": [0.85, 0.5]},
    {"target": "confirm.png", "position": [0.85, 0.5]},
    {"target": "detect.png", "wait": 0, "position": [0.85, 0.85]},
    {"target": "detect.png", "wait": 0, "position": [0.85, 0.85]},
    {"target": "detect.png", "wait": 0, "position": [0.85, 0.85]},
    {"target": "confirm2.png", "wait": 1, "position": [0.85, 0.85]},
    {"target": "confirm3.png", "wait": 0.5, "position": [0.85, 0.85]},
    {"target": "exit.png", "position": "right"}
  ]
}

def pos_to_str(pos):
    if isinstance(pos, list):
        return ",".join(map(str, pos))
    return pos

def add_scenario():
    base_actions = [
        {
            "key": data["baseAction"]["key"],
            "action": data["baseAction"]["action"],
            "wait": data["baseAction"]["wait"]
        }
    ]

    steps = []
    for step in data["scenario"]:
        steps.append({
            "key": data["baseAction"]["key"],  # baseAction의 key로 통일
            "target": step["target"],
            "position": pos_to_str(step.get("position")),
            "wait": step.get("wait", 0.5),
            "threshold": None,
            "min_match_count": None,
            "method": None
        })

    add_scenario_to_db("scenarios/scenario.db", base_id=1, base_actions=base_actions, steps=steps)
    print("DB 시나리오 추가 완료.")

if __name__ == "__main__":
    add_scenario()
