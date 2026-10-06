import sqlite3

conn = sqlite3.connect('jarvis.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print(f"✓ Database has {len(tables)} tables:")
for table in tables:
    print(f"  - {table}")
conn.close()
