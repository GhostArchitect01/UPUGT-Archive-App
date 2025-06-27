# fetcher/thread_downloader.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
import time
import logging

from config import HTML_RAW_DIR, FORUM_BASE_URL, FORUM_SECTION, LOG_FILE_PATH, FORCE_DOWNLOAD

# Ensure HTML output directory exists
os.makedirs(HTML_RAW_DIR, exist_ok=True)

# Logger setup
logger = logging.getLogger("ThreadDownloader")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(LOG_FILE_PATH)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def construct_thread_url(thread_id):
    return f"{FORUM_BASE_URL}?id={FORUM_SECTION}&thread={thread_id}"

def download_thread(thread_id):
    url = construct_thread_url(thread_id)
    output_path = os.path.join(HTML_RAW_DIR, f"thread_{thread_id}.html")

    if os.path.exists(output_path) and not FORCE_DOWNLOAD:
        logger.info(f"Skipping download for thread {thread_id}: File already exists and FORCE_DOWNLOAD is False.")
        return True

    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            logger.info(f"Downloaded thread {thread_id}")
            return True
        else:
            logger.warning(f"Thread {thread_id} returned status {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Failed to download thread {thread_id}: {e}")
        return False

def download_threads(thread_ids):
    """
    Downloads a list of threads.
    """
    print(f"Downloading {len(thread_ids)} threads...")
    for thread_id in thread_ids:
        logger.info(f"Fetching thread {thread_id}")
        download_thread(thread_id)
        time.sleep(1.0)  # Avoid hammering the site
    print("Download complete.")

def main():
    if len(sys.argv) < 2:
        print("Usage: python thread_downloader.py <id1> <id2> ...")
        return

    try:
        thread_ids = [int(arg) for arg in sys.argv[1:]]
    except ValueError:
        print("Error: Thread IDs must be integers.")
        return

    download_threads(thread_ids)

if __name__ == "__main__":
    main()
