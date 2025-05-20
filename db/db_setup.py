import os
import sqlite3

db_folder = os.path.join("scenarios")
os.makedirs(db_folder, exist_ok=True)

db_path = os.path.join(db_folder, "scenario.db")

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# baseAction 테이블: base_id 그룹 + key (복합 PK)
cur.execute("""
CREATE TABLE IF NOT EXISTS baseAction (
    base_id INTEGER NOT NULL,
    key TEXT NOT NULL,
    action TEXT NOT NULL,
    wait REAL DEFAULT 0.5,
    PRIMARY KEY (base_id, key)
)
""")

# scenario 테이블: base_id + key 포함
cur.execute("""
CREATE TABLE IF NOT EXISTS scenario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    base_id INTEGER NOT NULL,
    key TEXT NOT NULL,
    target TEXT NOT NULL,
    position TEXT,
    wait REAL,
    threshold REAL,
    min_match_count INTEGER,
    method TEXT,
    FOREIGN KEY (base_id) REFERENCES baseAction(base_id)
)
""")

conn.commit()
conn.close()

print("✅ DB 세팅 완료")
