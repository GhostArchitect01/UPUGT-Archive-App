import re
from datetime import datetime

def get_anchor_date(html: str) -> datetime:
    """
    Extracts the current server date from the forum HTML.
    Format: 'The current time is Mon May 19 16:52:12 2025'
    """
    match = re.search(r'The current time is (\w{3}) (\w{3}) (\d{1,2}) (\d{2}:\d{2}:\d{2}) (\d{4})', html)
    if not match:
        raise ValueError("Anchor date not found in HTML")
    dow, month, day, time_str, year = match.groups()
    return datetime.strptime(f"{month} {day} {year} {time_str}", "%b %d %Y %H:%M:%S")

def infer_year(anchor: datetime, post_dow: str, post_date_str: str) -> datetime:
    """
    Given the anchor date, post weekday (abbr like 'Wed'), and a string like 'Mar 19 14:16:08',
    infer the full datetime by matching against the anchor.
    """
    for year in reversed(range(2008, anchor.year + 1)):
        try:
            dt = datetime.strptime(f"{post_date_str} {year}", "%b %d %H:%M:%S %Y")
            if dt.strftime("%a") == post_dow and dt <= anchor:
                return dt
        except ValueError:
            continue
    raise ValueError(f"No matching year for {post_dow}, {post_date_str}")
