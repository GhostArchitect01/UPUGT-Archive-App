import os
import sys
import sqlite3
import re


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "forum.db")
TEXT_PHRASED_DIR = os.path.join(BASE_DIR, "text_phrased")

def insert_thread_to_db(thread_id, conn):
    file_path = os.path.join(TEXT_PHRASED_DIR, f"thread_{thread_id}.txt")
    if not os.path.exists(file_path):
        print(f"[!] Thread {thread_id} file not found.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    thread_title = ""
    posts = []
    current_post_data = {}
    current_content_lines = []
    in_post_content = False

    for line in lines:
        stripped_line = line.strip()

        if stripped_line == "=== THREAD TITLE ===":
            continue
        elif stripped_line == "=== END TITLE ===":
            continue
        elif not thread_title and stripped_line and not stripped_line.startswith("PostID"):
            thread_title = stripped_line
        elif stripped_line.startswith("PostID"):
            # Always treat PostID as the start of a new post, regardless of in_post_content
            # If we were processing a post, save it before starting a new one
            # If we were processing a post, save it before starting a new one
            if current_post_data and "post_id" in current_post_data:
                current_post_data["content"] = "\n".join(current_content_lines).strip()
                posts.append(current_post_data)

            # Start new post
            current_post_data = {}
            current_content_lines = []
            in_post_content = False

            match = re.match(r"PostIDs? (\d+)", stripped_line)
            if match:
                current_post_data["post_id"] = int(match.group(1))
            else:
                print(f"Error: Could not extract PostID from '{stripped_line}' in thread {thread_id}")
                # Skip this malformed post entry
                current_post_data = {}
                continue
        elif stripped_line.startswith("ThreadID:") and not in_post_content:
            try:
                current_post_data["thread_id"] = int(stripped_line.split(":", 1)[1].strip())
            except ValueError:
                print(f"Error converting ThreadID to int: '{stripped_line}' in thread {thread_id}")
                continue
        elif stripped_line.startswith("Poster:") and not in_post_content:
            current_post_data["poster"] = stripped_line.split(":", 1)[1].strip()
        elif stripped_line.startswith("Tag:") and not in_post_content:
            current_post_data["tag"] = stripped_line.split(":", 1)[1].strip()
        elif stripped_line.startswith("RawTime:") and not in_post_content:
            current_post_data["raw_timestamp"] = stripped_line.split(":", 1)[1].strip()
        elif stripped_line.startswith("ISOTime:") and not in_post_content:
            current_post_data["iso_timestamp"] = stripped_line.split(":", 1)[1].strip()
        elif stripped_line.startswith("Content:"):
            in_post_content = True
        elif stripped_line == "=== END POST ===":
            if current_post_data and "post_id" in current_post_data: # Ensure it's a valid post before appending
                current_post_data["content"] = "\n".join(current_content_lines).strip()
                posts.append(current_post_data)
            current_post_data = {}
            current_content_lines = []
            in_post_content = False
        elif in_post_content:
            current_content_lines.append(line)
        else:
            # This handles lines that are not part of a post and not the thread title
            # For example, empty lines or unexpected lines between posts
            pass

    # Handle the last post if the file doesn't end with "=== END POST ==="
    if current_post_data and "post_id" in current_post_data:
        current_post_data["content"] = "\n".join(current_content_lines).strip()
        posts.append(current_post_data)

    # Insert into DB
    cursor = conn.cursor()
    for post in posts:
        # Ensure all required keys are present before insertion
        required_keys = ["post_id", "thread_id", "poster", "tag", "raw_timestamp", "iso_timestamp", "content"]
        if not all(key in post for key in required_keys):
            print(f"Skipping incomplete post from thread {thread_id}: {post}")
            continue

        cursor.execute("""
            INSERT OR IGNORE INTO posts (
                post_id, thread_id, thread_title, poster, tag,
                raw_timestamp, iso_timestamp, content
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            post["post_id"],
            post["thread_id"],
            thread_title,
            post["poster"],
            post["tag"],
            post["raw_timestamp"],
            post["iso_timestamp"],
            post["content"]
        ))
    conn.commit()
    print(f"[✓] Inserted {len(posts)} posts from thread {thread_id}")

def batch_insert(thread_ids):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            thread_id INTEGER,
            thread_title TEXT,
            poster TEXT,
            tag TEXT,
            raw_timestamp TEXT,
            iso_timestamp TEXT,
            content TEXT,
            UNIQUE(thread_id, post_id)
        );
    """)
    for thread_id in thread_ids:
        insert_thread_to_db(thread_id, conn)
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python inserter/db_inserter.py <id1> <id2> ...")
    else:
        try:
            thread_ids = [int(arg) for arg in sys.argv[1:]]
            batch_insert(thread_ids)
        except ValueError:
            print("Error: Thread IDs must be integers.")
