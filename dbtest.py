import sqlite3

# SQLite 데이터베이스에 연결
conn = sqlite3.connect('users.db')
c = conn.cursor()

# users 테이블에서 모든 데이터를 선택
c.execute("SELECT * FROM users")

# 모든 행을 가져와서 출력
rows = c.fetchall()
for row in rows:
    print(row)

# 연결을 닫음
conn.close()