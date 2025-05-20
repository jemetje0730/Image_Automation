import os
import sqlite3

db_folder = os.path.join("scenarios")
os.makedirs(db_folder, exist_ok=True)  # 폴더가 없으면 생성

db_path = os.path.join(db_folder, "scenario.db")

conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS baseAction (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL,
    action TEXT NOT NULL,
    wait REAL DEFAULT 0.5
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS scenario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    base_id INTEGER NOT NULL,
    target TEXT NOT NULL,
    position TEXT,
    wait REAL,
    threshold REAL,
    min_match_count INTEGER,
    method TEXT,
    FOREIGN KEY (base_id) REFERENCES baseAction(id)
)
""")

cur.execute("INSERT INTO baseAction (key, action, wait) VALUES (?, ?, ?)", ("A", "click", 0.5))
base_id = cur.lastrowid
cur.execute("INSERT INTO scenario (base_id, target, position, wait) VALUES (?, ?, ?, ?)",
            (base_id, "lidar.png", "center", None))

conn.commit()
conn.close()
print("✅ DB 세팅 완료.")
