import sqlite3

def load_scenario_from_db(db_path="scenario.db", base_id=1):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # baseAction 불러오기
    cur.execute("SELECT key, action, wait FROM baseAction WHERE base_id=?", (base_id,))
    base_actions = cur.fetchall()
    if not base_actions:
        raise ValueError(f"base_id {base_id} 없음")

    base_action_dict = {key: {"action": action, "wait": wait} for key, action, wait in base_actions}

    # scenario 불러오기 (action 컬럼 포함)
    cur.execute("""
        SELECT key, target, position, wait, threshold, min_match_count, method, action
        FROM scenario WHERE base_id=? ORDER BY id
    """, (base_id,))

    steps = []
    for row in cur.fetchall():
        key, target, position, wait, threshold, min_match_count, method, action = row
        if key not in base_action_dict:
            raise ValueError(f"scenario에 정의된 key '{key}'가 baseAction에 없습니다.")

        # 단계별 action이 있으면 우선 사용, 없으면 baseAction 사용
        step_action = action if action else base_action_dict[key]["action"]
        step_wait = wait if wait is not None else base_action_dict[key]["wait"]

        step = {
            "key": key,
            "action": step_action,
            "wait": step_wait,
            "target": target,
            "position": position,
            "threshold": threshold,
            "min_match_count": min_match_count,
            "method": method
        }
        steps.append(step)

    conn.close()
    return steps

def add_scenario_to_db(db_path, base_id, base_actions=None, steps=[]):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # base_actions가 있으면만 insert
    if base_actions:
        for base_action in base_actions:
            cur.execute("""
                INSERT OR IGNORE INTO baseAction (base_id, key, action, wait)
                VALUES (?, ?, ?, ?)
            """, (
                base_id,
                base_action.get("key"),
                base_action.get("action"),
                base_action.get("wait", 0.5)
            ))

    # 시나리오 단계 삽입
    for step in steps:
        cur.execute("""
            INSERT INTO scenario (
                base_id, key, action, target, position, wait,
                threshold, min_match_count, method
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            base_id,
            step.get("key"),
            step.get("action"),  # 여기 action 추가
            step.get("target"),
            step.get("position"),
            step.get("wait", 0.5),
            step.get("threshold"),
            step.get("min_match_count"),
            step.get("method")
        ))

    conn.commit()
    conn.close()


def delete_scenario_steps_from_db(db_path, base_id):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # scenario 테이블에서만 삭제
    cur.execute("DELETE FROM scenario WHERE base_id = ?", (base_id,))

    conn.commit()
    conn.close()
    print(f"✅ base_id={base_id}의 시나리오 단계만 삭제 완료 (baseAction은 유지됨)")
