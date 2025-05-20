import sqlite3

db_path = "scenarios/scenario.db"
base_id = 1  # 삭제할 시나리오 ID

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 삭제 전 확인
print("Before:")
for row in cur.execute("SELECT * FROM scenario WHERE base_id = ?", (base_id,)):
    print(row)

# scenario 테이블에서만 삭제 (baseAction은 유지)
cur.execute("DELETE FROM scenario WHERE base_id = ?", (base_id,))
conn.commit()

# 삭제 후 확인
print("\nAfter:")
for row in cur.execute("SELECT * FROM scenario WHERE base_id = ?", (base_id,)):
    print(row)

conn.close()
