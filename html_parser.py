import os
import sys
import re
from bs4 import BeautifulSoup
from datetime import datetime

# Fix for missing '__file__' on some environments
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.timestamp_utils import infer_year
from config import HTML_RAW_DIR, TEXT_PHRASED_DIR, FORCE_PARSE

def extract_posts(soup, thread_id):
    posts = []

    full_text = soup.get_text()
    anchor_match = re.search(r"The current time is (\w{3}) (\w{3}) (\d{1,2}) (\d{2}:\d{2}:\d{2}) (\d{4})", full_text)
    if not anchor_match:
        print(f"[!] Could not find anchor timestamp in thread {thread_id}")
        return posts

    anchor = datetime.strptime(" ".join(anchor_match.groups()[1:]), "%b %d %H:%M:%S %Y")

    for row in soup.find_all("tr"):
        tds = row.find_all("td")
        if len(tds) != 2:
            continue
        if not tds[0].get_text(strip=True):
            continue
        if not tds[1].find("font"):
            continue

        try:
            username_lines = list(tds[0].stripped_strings)
            username = username_lines[0].lower()
            member_tag = username_lines[1] if len(username_lines) > 1 else "Unknown"

            raw_timestamp = tds[1].find("font").get_text(strip=True)
            dow, rest = raw_timestamp.split(" ", 1)
            iso_timestamp = infer_year(anchor, dow, rest).isoformat()

            # Get post content and remove the timestamp <font> tag
            content_td = tds[1].decode_contents()
            soup_block = BeautifulSoup(content_td, 'html.parser')
            font_tag = soup_block.find("font")
            if font_tag:
                font_tag.extract()

            for a in soup_block.find_all('a'):
                href = a.get('href')
                label = a.get_text(strip=True)
                if href:
                    a.replace_with(f"[{label}]({href})")

            content = soup_block.get_text(separator="\n", strip=True)

            posts.append({
                "thread_id": thread_id,
                "username": username,
                "member_tag": member_tag,
                "raw_timestamp": raw_timestamp,
                "iso_timestamp": iso_timestamp,
                "content": content
            })

        except Exception as e:
            print(f"[!] Error parsing post in thread {thread_id}: {e}")
            continue

    return posts

def parse_thread_html(thread_id):
    html_path = os.path.join(HTML_RAW_DIR, f"thread_{thread_id}.html")
    output_path = os.path.join(TEXT_PHRASED_DIR, f"thread_{thread_id}.txt")

    

    if not os.path.exists(html_path):
        print(f"[!] HTML not found for thread {thread_id}")
        return

    with open(html_path, 'r', encoding='utf-8', errors='ignore') as file:
        soup = BeautifulSoup(file.read(), 'html.parser')

    # Extract the thread title
    title_tag = soup.find("title")
    thread_title = title_tag.get_text(strip=True) if title_tag else f"Thread {thread_id}"

    posts = extract_posts(soup, thread_id)
    if not posts:
        print(f"[!] No posts found in thread {thread_id}")
        return

    os.makedirs(TEXT_PHRASED_DIR, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as out:
        out.write(f"=== THREAD TITLE ===\n{thread_title}\n=== END TITLE ===\n\n")
        for i, post in enumerate(posts, 1):
            out.write(f"PostID {i}\n")
            out.write(f"ThreadID: {post['thread_id']}\n")
            out.write(f"Poster: {post['username']}\n")
            out.write(f"Tag: {post['member_tag']}\n")
            out.write(f"RawTime: {post['raw_timestamp']}\n")
            out.write(f"ISOTime: {post['iso_timestamp']}\n")
            out.write(f"Content:\n{post['content']}\n")
            out.write(f"=== END POST ===\n\n")

    print(f"[✓] Parsed thread {thread_id} → {output_path}")

def batch_parse(thread_ids):
    """
    Parses a list of threads.
    """
    for thread_id in thread_ids:
        parse_thread_html(thread_id)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python html_parser.py <id1> <id2> ...")
    else:
        try:
            thread_ids = [int(arg) for arg in sys.argv[1:]]
            batch_parse(thread_ids)
        except ValueError:
            print("Error: Thread IDs must be integers.")
