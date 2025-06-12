import os
import sqlite3

def setup_db():
    db_folder = os.path.join("scenarios")
    os.makedirs(db_folder, exist_ok=True)

    db_path = os.path.join(db_folder, "scenario.db")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS baseAction (
        base_id INTEGER NOT NULL,
        key TEXT NOT NULL,
        action TEXT NOT NULL,
        wait REAL DEFAULT 0.5,
        PRIMARY KEY (base_id, key)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS scenario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        base_id INTEGER NOT NULL,
        key TEXT NOT NULL,
        action TEXT,
        target TEXT NOT NULL,
        position TEXT,
        wait REAL,
        threshold REAL,
        min_match_count INTEGER,
        method TEXT,
        FOREIGN KEY (base_id) REFERENCES baseAction(base_id)
    )
    """)

    cur.execute("""
    INSERT OR IGNORE INTO baseAction (base_id, key, action, wait)
    VALUES (1, 'A', 'click', 0.5)
    """)

    cur.execute("""
    INSERT OR IGNORE INTO baseAction (base_id, key, action, wait)
    VALUES (1, 'R', 'screen', 0.5)
    """)

    conn.commit()
    conn.close()

    print("✅ DB 세팅 완료 및 기본 baseAction 삽입 (base_id=1, A/R)")

if __name__ == "__main__":
    setup_db()
