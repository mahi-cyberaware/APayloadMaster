import sqlite3
import json
from datetime import datetime
import hashlib

class PayloadDB:
    def __init__(self, db_path="payloads.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Payloads table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                platform TEXT,
                lhost TEXT,
                lport INTEGER,
                encryption_type TEXT,
                obfuscation_level TEXT,
                hash TEXT,
                size INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                payload_id INTEGER,
                session_id TEXT,
                ip_address TEXT,
                platform TEXT,
                user_agent TEXT,
                connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP,
                FOREIGN KEY (payload_id) REFERENCES payloads (id)
            )
        ''')
        
        # Downloads table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                payload_id INTEGER,
                download_url TEXT,
                ip_address TEXT,
                user_agent TEXT,
                downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (payload_id) REFERENCES payloads (id)
            )
        ''')
        
        self.conn.commit()
    
    def add_payload(self, payload_data):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO payloads (filename, filepath, platform, lhost, lport, 
                                 encryption_type, obfuscation_level, hash, size, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            payload_data['filename'],
            payload_data['filepath'],
            payload_data.get('platform'),
            payload_data.get('lhost'),
            payload_data.get('lport'),
            payload_data.get('encryption_type'),
            payload_data.get('obfuscation_level'),
            payload_data.get('hash'),
            payload_data.get('size'),
            json.dumps(payload_data.get('metadata', {}))
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_payload(self, payload_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM payloads WHERE id = ?', (payload_id,))
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'filename': row[1],
                'filepath': row[2],
                'platform': row[3],
                'lhost': row[4],
                'lport': row[5],
                'encryption_type': row[6],
                'obfuscation_level': row[7],
                'hash': row[8],
                'size': row[9],
                'created_at': row[10],
                'metadata': json.loads(row[11]) if row[11] else {}
            }
        return None
    
    def get_all_payloads(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM payloads ORDER BY created_at DESC')
        rows = cursor.fetchall()
        return [{
            'id': row[0],
            'filename': row[1],
            'filepath': row[2],
            'platform': row[3],
            'lhost': row[4],
            'lport': row[5],
            'created_at': row[10]
        } for row in rows]
    
    def get_recent_payloads(self, limit=10):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM payloads ORDER BY created_at DESC LIMIT ?', (limit,))
        rows = cursor.fetchall()
        return [{
            'id': row[0],
            'filename': row[1],
            'filepath': row[2],
            'platform': row[3],
            'lhost': row[4],
            'lport': row[5],
            'created_at': row[10]
        } for row in rows]
    
    def add_session(self, payload_id, session_data):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO sessions (payload_id, session_id, ip_address, platform, user_agent)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            payload_id,
            session_data.get('session_id'),
            session_data.get('ip_address'),
            session_data.get('platform'),
            session_data.get('user_agent')
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def add_download(self, payload_id, download_data):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO downloads (payload_id, download_url, ip_address, user_agent)
            VALUES (?, ?, ?, ?)
        ''', (
            payload_id,
            download_data.get('download_url'),
            download_data.get('ip_address'),
            download_data.get('user_agent')
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_stats(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM payloads')
        payload_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM sessions')
        session_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM downloads')
        download_count = cursor.fetchone()[0]
        
        return f"Payloads: {payload_count} | Sessions: {session_count} | Downloads: {download_count}"
    
    def close(self):
        self.conn.close()
