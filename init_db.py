import sqlite3
import os
from datetime import datetime

def init_database():
    # Ensure database directory exists
    if not os.path.exists('database'):
        os.makedirs('database')
    
    # Connect to database
    conn = sqlite3.connect('database/db.sqlite3')
    cur = conn.cursor()
    
    try:
        # Drop existing tables
        cur.execute('DROP TABLE IF EXISTS logs')
        cur.execute('DROP TABLE IF EXISTS user')
        cur.execute('DROP TABLE IF EXISTS slots')
        
        # Create tables with correct schema
        cur.execute('''
            CREATE TABLE user (
                rfid TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                amount REAL DEFAULT 0.0
            )
        ''')
        
        cur.execute('''
            CREATE TABLE logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rfid TEXT NOT NULL,
                in_time TEXT NOT NULL,
                out_time TEXT,
                duration TEXT,
                amount REAL,
                payment_status TEXT DEFAULT 'unpaid',
                FOREIGN KEY (rfid) REFERENCES user (rfid)
            )
        ''')
        
        cur.execute('''
            CREATE TABLE slots (
                slot_id INTEGER PRIMARY KEY,
                status TEXT DEFAULT 'free'
            )
        ''')
        
        # Create default users
        cur.execute("INSERT INTO user (rfid, name, role) VALUES (?, ?, ?)", 
                    ('10', 'Owner', 'owner'))
        cur.execute("INSERT INTO user (rfid, name, role) VALUES (?, ?, ?)", 
                    ('1', 'User', 'user'))
        
        # Create 8 slots
        for i in range(1, 9):
            cur.execute('INSERT INTO slots (slot_id, status) VALUES (?, ?)', 
                       (i, 'free'))
        
        conn.commit()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    init_database() 