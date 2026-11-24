"""
MySpeedTest - History Manager Module
Manages SQLite database storage for speed test results, providing query,
deletion, aggregation statistics, and CSV export capabilities.
"""

import sqlite3
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Any
import os

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "speedtest.db")


def get_db_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Create a thread-safe database connection."""
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """Initialize SQLite database tables if they do not exist."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                download_mbps REAL NOT NULL,
                upload_mbps REAL NOT NULL,
                ping_ms REAL NOT NULL,
                jitter_ms REAL NOT NULL,
                peak_download REAL,
                peak_upload REAL,
                ip_address TEXT,
                isp TEXT,
                server_name TEXT,
                server_location TEXT
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON test_history (timestamp DESC)")
        conn.commit()


def save_test_result(
    download_mbps: float,
    upload_mbps: float,
    ping_ms: float,
    jitter_ms: float,
    peak_download: Optional[float] = None,
    peak_upload: Optional[float] = None,
    ip_address: str = "Unknown",
    isp: str = "Unknown",
    server_name: str = "Unknown",
    server_location: str = "Unknown",
    db_path: str = DEFAULT_DB_PATH
) -> int:
    """Insert a completed speed test result into SQLite history."""
    init_db(db_path)
    now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    peak_dl = peak_download if peak_download is not None else download_mbps
    peak_ul = peak_upload if peak_upload is not None else upload_mbps

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO test_history (
                timestamp, download_mbps, upload_mbps, ping_ms, jitter_ms,
                peak_download, peak_upload, ip_address, isp, server_name, server_location
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            now_iso,
            round(float(download_mbps), 2),
            round(float(upload_mbps), 2),
            round(float(ping_ms), 2),
            round(float(jitter_ms), 2),
            round(float(peak_dl), 2),
            round(float(peak_ul), 2),
            str(ip_address),
            str(isp),
            str(server_name),
            str(server_location)
        ))
        conn.commit()
        return cursor.lastrowid or 0


def get_all_history(db_path: str = DEFAULT_DB_PATH) -> pd.DataFrame:
    """Retrieve full speed test history as a Pandas DataFrame ordered by latest first."""
    init_db(db_path)
    query = """
        SELECT 
            id,
            timestamp,
            download_mbps,
            upload_mbps,
            ping_ms,
            jitter_ms,
            peak_download,
            peak_upload,
            ip_address,
            isp,
            server_name,
            server_location
        FROM test_history
        ORDER BY id DESC
    """
    with get_db_connection(db_path) as conn:
        df = pd.read_sql_query(query, conn)
    return df


def delete_test_record(record_id: int, db_path: str = DEFAULT_DB_PATH) -> bool:
    """Delete an individual test record by primary key ID."""
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM test_history WHERE id = ?", (record_id,))
        conn.commit()
        return cursor.rowcount > 0


def clear_all_history(db_path: str = DEFAULT_DB_PATH) -> bool:
    """Clear all records from test history table."""
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM test_history")
        conn.commit()
        return True


def get_summary_stats(db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """Calculate summary aggregated metrics across all recorded tests."""
    df = get_all_history(db_path)
    if df.empty:
        return {
            "total_tests": 0,
            "avg_download": 0.0,
            "avg_upload": 0.0,
            "avg_ping": 0.0,
            "best_download": 0.0,
            "best_upload": 0.0,
            "lowest_ping": 0.0
        }

    return {
        "total_tests": len(df),
        "avg_download": round(df["download_mbps"].mean(), 2),
        "avg_upload": round(df["upload_mbps"].mean(), 2),
        "avg_ping": round(df["ping_ms"].mean(), 2),
        "best_download": round(df["download_mbps"].max(), 2),
        "best_upload": round(df["upload_mbps"].max(), 2),
        "lowest_ping": round(df["ping_ms"].min(), 2)
    }


def export_csv_data(db_path: str = DEFAULT_DB_PATH) -> str:
    """Export complete history data as formatted CSV string."""
    df = get_all_history(db_path)
    return df.to_csv(index=False)

