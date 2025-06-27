import sqlite3
import os

DB_PATH = os.path.join("database", "forum.db")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS threads (
    thread_id TEXT PRIMARY KEY,
    thread_title TEXT,
    op_username TEXT,
    first_post_date_raw TEXT,
    first_post_date_iso TEXT,
    last_post_date_raw TEXT,
    last_post_date_iso TEXT,
    post_count INTEGER
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS posts (
    post_id TEXT PRIMARY KEY,
    thread_id TEXT,
    poster TEXT,
    member_tag TEXT,
    timestamp_raw TEXT,
    timestamp_iso TEXT,
    content TEXT,
    FOREIGN KEY (thread_id) REFERENCES threads(thread_id)
);
''')

conn.commit()
conn.close()
