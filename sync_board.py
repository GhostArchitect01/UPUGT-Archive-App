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

def parse_thread_ids(html_content):
    """Parses the HTML to extract thread IDs."""
    if not html_content:
        return []
    
    print("Parsing thread IDs from index page...")
    soup = BeautifulSoup(html_content, 'html.parser')
    thread_ids = set()
    
    # Find all links and look for the thread ID pattern
    for a_tag in soup.find_all('a', href=True):
        match = re.search(r'thread=(\d+)', a_tag['href'])
        if match:
            thread_ids.add(int(match.group(1)))
            
    print(f"Found {len(thread_ids)} unique thread IDs on the index page.")
    return list(thread_ids)

def get_existing_thread_ids():
    """Queries the database to get all unique thread IDs already stored."""
    if not os.path.exists(DB_PATH):
        print("Database not found. Returning no existing threads.")
        return []
        
    print("Querying database for existing threads...")
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT thread_id FROM posts")
            existing_ids = {row[0] for row in cursor.fetchall()}
        print(f"Found {len(existing_ids)} existing threads in the database.")
        return existing_ids
    except sqlite3.Error as e:
        print(f"[!] Database error: {e}")
        return []

def main():
    """Main function to sync the board."""
    html_content = fetch_index_page()
    if not html_content:
        return

    online_thread_ids = parse_thread_ids(html_content)
    if not online_thread_ids:
        print("No thread IDs found on the index page. Exiting.")
        return

    print(f"\nFound {len(online_thread_ids)} threads on the index page.")
    print("Processing all threads to check for new posts...")
    run_pipeline(online_thread_ids)

if __name__ == "__main__":
    main()
