# TUI App

This application is designed to fetch, parse, and store forum thread data. It consists of several modules that work together in a pipeline: `fetcher` (downloads raw HTML), `formatter` (parses HTML into structured text), and `inserter` (stores data into a SQLite database).

## Setup and Initialization

Follow these steps to set up and initialize the application:

### 1. Prerequisites

Ensure you have Python 3 and `pip` installed.

Ensure you have SQLite.

### 2. Install Dependencies

Navigate to the project's root directory and install the required Python packages:

```bash
pip install -r requirements.txt
```

### 3. Initialize the Database

The application uses a SQLite database to store thread and post information. You need to initialize the database schema before first use.

```bash
python init_db.py
```

This will create a `forum.db` file in the `database/` directory with the necessary tables.

### 4. Configuration

The `config.py` file contains important configuration variables, such as paths for raw HTML, processed text, logs, and database files, as well as forum-specific settings. Review and adjust these settings as needed.

### 5. Running the Pipeline

The `pipeline.py` script orchestrates the entire process of downloading, parsing, and inserting thread data. You can specify individual thread IDs or a range of IDs to process.

#### Examples:

- **Process a single thread:**
  ```bash
  python pipeline.py 12345
  ```

- **Process multiple specific threads:**
  ```bash
  python pipeline.py 12345 67890 11223
  ```

- **Process a range of threads:**
  ```bash
  python pipeline.py 93500-93600
  ```

- **Process a combination of single threads and ranges:**
  ```bash
  python pipeline.py 100 200-205 300
  ```

### 6. Manual Operations (Advanced)

While `pipeline.py` handles the full workflow, you can also run individual stages manually for debugging or specific tasks:

- **Download raw HTML:**
  ```bash
  python fetcher/thread_downloader.py <thread_id> [thread_id...]
  ```

- **Parse HTML to text:**
  ```bash
  python formatter/html_parser.py <thread_id> [thread_id...]
  ```

- **Insert data into DB:**
  (Note: The `inserter/db_inserter.py` script is typically called by `pipeline.py` and expects parsed data to be available. It's not designed for direct manual execution with thread IDs in the same way as the fetcher and formatter.)

### 7. Cron Job (Optional)

The `cronjob.txt` file contains an example cron job entry that can be used to automate the `sync_board.py` script. This script is likely responsible for regularly synchronizing data.

To add this cron job, you would typically use the `crontab` command:

```bash
crontab -e
```
Then, add the line from `cronjob.txt` to your crontab file. Remember to adjust paths if your setup differs.

```
2 3 * * * /data/data/com.termux/files/usr/bin/python /data/data/com.termux/files/home/tui_app/sync_board.py >> /data/data/com.termux/files/home/tui_app/logs/sync_board_cron.log 2>&1
```

---
