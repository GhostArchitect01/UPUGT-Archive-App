import sys
from fetcher.thread_downloader import download_threads
from formatter.html_parser import batch_parse
from inserter.db_inserter import batch_insert

def run_pipeline(thread_ids):
    """
    Runs the full download, parse, and insert pipeline for a list of threads.
    """
    print(f"Starting pipeline for {len(thread_ids)} threads...")
    
    # Stage 1: Download
    print("\n----- STAGE 1: DOWNLOADING -----")
    download_threads(thread_ids)
    
    # Stage 2: Parse
    print("\n----- STAGE 2: PARSING -----")
    batch_parse(thread_ids)
    
    # Stage 3: Insert
    print("\n----- STAGE 3: INSERTING -----")
    batch_insert(thread_ids)
    
    print("\nPipeline complete.")

def parse_thread_id_args(args):
    thread_ids = set()
    for arg in args:
        if '-' in arg:
            start, end = map(int, arg.split('-'))
            thread_ids.update(range(start, end + 1))
        else:
            thread_ids.add(int(arg))
    return sorted(list(thread_ids))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pipeline.py <id1> <id2>... or <start-end>")
    else:
        try:
            thread_ids = parse_thread_id_args(sys.argv[1:])
            run_pipeline(thread_ids)
        except ValueError:
            print("Error: Thread IDs must be integers or valid ranges (e.g., 1-5).")
