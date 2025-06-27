import os

# === PATHS ===
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

HTML_RAW_DIR = os.path.join(PROJECT_ROOT, "html_raw")
TEXT_PHRASED_DIR = os.path.join(PROJECT_ROOT, "text_phrased")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
DB_DIR = os.path.join(PROJECT_ROOT, "database")
SCHEMA_DIR = os.path.join(PROJECT_ROOT, "schema")

FORUM_DB_PATH = os.path.join(DB_DIR, "forum.db")
METADATA_DB_PATH = os.path.join(DB_DIR, "metadata.db")

FORUM_SCHEMA_PATH = os.path.join(SCHEMA_DIR, "forum_schema.sql")
METADATA_SCHEMA_PATH = os.path.join(SCHEMA_DIR, "metadata_schema.sql")

# === FLAGS & TOGGLES ===
OVERWRITE_MODE = False      # If True, re-inserts or overwrites duplicates in DB
LOG_LEVEL = "INFO"          # DEBUG, INFO, WARNING, ERROR
FORCE_DOWNLOAD = False      # Override download skipping logic
FORCE_PARSE = False         # Override parsing skip checks

# === FORUM CONFIG ===
FORUM_BASE_URL = "http://utopiaforums.com/boardthread"
FORUM_SECTION = "politics"  # Hardcoded for now — could be generalized later

# === LOGGING DEFAULTS ===
LOG_FILE_NAME = "utopia_tui.log"
LOG_FILE_PATH = os.path.join(LOGS_DIR, LOG_FILE_NAME)
