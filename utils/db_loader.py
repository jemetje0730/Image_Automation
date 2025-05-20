import sqlite3

def load_scenario_from_db(db_path="scenario.db", base_id=1):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # baseAction 불러오기
    cur.execute("SELECT key, action, wait FROM baseAction WHERE id=?", (base_id,))
    base = cur.fetchone()
    if not base:
        raise ValueError(f"base_id {base_id} 없음")

    base_action = {"key": base[0], "action": base[1], "wait": base[2]}

    # scenario 불러오기
    cur.execute("SELECT target, position, wait, threshold, min_match_count, method FROM scenario WHERE base_id=? ORDER BY id", (base_id,))
    steps = []
    for row in cur.fetchall():
        step = base_action.copy()
        step["target"] = row[0]
        if row[1]: step["position"] = row[1]
        if row[2] is not None: step["wait"] = row[2]
        if row[3] is not None: step["threshold"] = row[3]
        if row[4] is not None: step["min_match_count"] = row[4]
        if row[5]: step["method"] = row[5]
        steps.append(step)

    conn.close()
    return steps

def add_scenario_to_db(db_path, base_id, base_action, steps):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # baseAction 삽입
    cur.execute('''
        INSERT OR REPLACE INTO baseAction (id, key, action, wait)
        VALUES (?, ?, ?, ?)
    ''', (base_id, base_action.get("key"), base_action.get("action"), base_action.get("wait")))

    # scenario 삽입
    for step in steps:
        cur.execute('''
            INSERT INTO scenario (base_id, target, position, wait, threshold, min_match_count, method)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            base_id,
            step.get("target"),
            step.get("position"),
            step.get("wait"),
            step.get("threshold"),
            step.get("min_match_count"),
            step.get("method"),
        ))

    conn.commit()
    conn.close()