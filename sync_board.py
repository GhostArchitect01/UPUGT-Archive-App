import requests
from bs4 import BeautifulSoup
import sqlite3
import os
import re
from pipeline import run_pipeline

# Configuration
FORUM_INDEX_URL = "http://utopiaforums.com/boardforum?id=politics"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "forum.db")

def fetch_index_page():
    """Fetches the HTML content of the forum index page."""
    print(f"Fetching index page: {FORUM_INDEX_URL}")
    try:
        response = requests.get(FORUM_INDEX_URL, timeout=15)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"[!] Error fetching index page: {e}")
        return None

def parse_thread_data(html_content):
    """Parses the HTML to extract thread IDs and their post counts."""
    if not html_content:
        return {}
    
    print("Parsing thread data from index page...")
    soup = BeautifulSoup(html_content, 'html.parser')
    thread_data = {} # {thread_id: post_count}
    
    # Find all table rows that are likely thread entries (excluding the header row)
    # The header row has class 'highlight'
    for row in soup.find_all('tr'):
        if 'class' in row.attrs and 'highlight' in row['class']:
            continue # Skip header row

        tds = row.find_all('td')
        if len(tds) >= 2: # Ensure there are at least two columns (topic and posts)
            a_tag = tds[0].find('a', href=True)
            if a_tag:
                match = re.search(r'thread=(\d+)', a_tag['href'])
                if match:
                    thread_id = int(match.group(1))
                    
                    try:
                        post_count = int(tds[1].get_text(strip=True))
                        thread_data[thread_id] = post_count
                    except ValueError:
                        # If post count is not a number, skip or log an error
                        print(f"[!] Could not parse post count for thread {thread_id}")
                        continue
            
    print(f"Found {len(thread_data)} unique threads with post counts on the index page.")
    return thread_data

def get_existing_thread_post_counts():
    """Queries the database to get the highest post ID for each thread."""
    if not os.path.exists(DB_PATH):
        print("Database not found. Returning no existing thread post counts.")
        return {}
        
    print("Querying database for existing thread post counts...")
    existing_thread_post_counts = {}
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            # Assuming post_id can be cast to INTEGER for MAX comparison
            cursor.execute("SELECT thread_id, MAX(CAST(SUBSTR(post_id, INSTR(post_id, ' ') + 1) AS INTEGER)) FROM posts GROUP BY thread_id")
            for row in cursor.fetchall():
                thread_id, max_post_id = row
                existing_thread_post_counts[int(thread_id)] = max_post_id
        print(f"Found post counts for {len(existing_thread_post_counts)} existing threads in the database.")
        return existing_thread_post_counts
    except sqlite3.Error as e:
        print(f"[!] Database error: {e}")
        return {}

def main():
    """Main function to sync the board."""
    html_content = fetch_index_page()
    if not html_content:
        return

    online_thread_data = parse_thread_data(html_content)
    if not online_thread_data:
        print("No thread data found on the index page. Exiting.")
        return

    existing_thread_post_counts = get_existing_thread_post_counts()
    
    threads_to_process = set()

    for thread_id, online_post_count in online_thread_data.items():
        if thread_id not in existing_thread_post_counts:
            print(f"New thread found: {thread_id}")
            threads_to_process.add(thread_id)
        else:
            db_post_count = existing_thread_post_counts[thread_id]
            if online_post_count > db_post_count:
                print(f"Thread {thread_id} has new posts: Online {online_post_count}, DB {db_post_count}")
                threads_to_process.add(thread_id)
            # else: print(f"Thread {thread_id} is up to date.") # Optional: for verbose logging

    if threads_to_process:
        sorted_threads = sorted(list(threads_to_process))
        print(f"Processing {len(sorted_threads)} threads (new or updated)...")
        run_pipeline(sorted_threads)
    else:
        print("No new or updated threads found on the index page.")

if __name__ == "__main__":
    main()
