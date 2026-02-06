import sqlite3
import json
from datetime import datetime

DB_NAME = 'notams.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS notams (
            id TEXT PRIMARY KEY,
            raw_text TEXT,
            decoded_json TEXT,
            location TEXT,
            start_time TEXT,
            end_time TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_notam(notam_dict):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute('''
            INSERT OR IGNORE INTO notams (id, raw_text, decoded_json, location, start_time, end_time)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            notam_dict.get('id'),
            notam_dict.get('raw_text'),
            json.dumps(notam_dict),
            notam_dict.get('location'),
            notam_dict.get('start_time'),
            notam_dict.get('end_time')
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving NOTAM: {e}")
        return False
    finally:
        conn.close()

def get_all_notams():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM notams ORDER BY created_at DESC')
    rows = c.fetchall()
    notams = []
    for row in rows:
        notams.append(dict(row))
    conn.close()
    return notams
