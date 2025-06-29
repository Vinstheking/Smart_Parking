import sqlite3
import os
from datetime import datetime, timedelta
import math

def format_duration(seconds):
    """Convert seconds to hours and minutes format"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours == 0:
        if minutes == 0:
            return f"{seconds} second{'s' if seconds != 1 else ''}"
        return f"{minutes} minute{'s' if minutes != 1 else ''} {seconds} second{'s' if seconds != 1 else ''}"
    return f"{hours} hour{'s' if hours != 1 else ''} {minutes} minute{'s' if minutes != 1 else ''}"

def calculate_parking_charge(seconds):
    """Calculate parking charge based on duration in seconds"""
    hours = seconds / 3600
    # First hour or part thereof: ₹50
    # Each additional hour or part thereof: ₹50
    if hours <= 1:
        return 50
    # Round up to nearest hour
    rounded_hours = math.ceil(hours)
    return 50 + ((rounded_hours - 1) * 50)

def add_sample_data():
    # Ensure database directory exists
    if not os.path.exists('database'):
        os.makedirs('database')
    
    conn = sqlite3.connect('database/db.sqlite3')
    cur = conn.cursor()

    try:
        # Add sample parking logs for the user (RFID: 1)
        now = datetime.now()
        user_logs = [
            # First log: 15 minutes parking, paid (₹50)
            ('1', 
             (now - timedelta(days=2, minutes=15)).strftime("%Y-%m-%d %H:%M:%S"),
             (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
             format_duration(15 * 60),  # 15 minutes in seconds
             calculate_parking_charge(15 * 60)),  # ₹50 (first hour or part thereof)
            
            # Second log: 1 hour 15 minutes parking, unpaid
            ('1',
             (now - timedelta(days=1, hours=1, minutes=15)).strftime("%Y-%m-%d %H:%M:%S"),
             (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
             format_duration(75 * 60),  # 1 hour 15 minutes in seconds
             0.00),  # Unpaid (should be ₹100)
            
            # Third log: 2 hours 35 minutes parking, paid
            ('1',
             (now - timedelta(hours=2, minutes=35)).strftime("%Y-%m-%d %H:%M:%S"),
             now.strftime("%Y-%m-%d %H:%M:%S"),
             format_duration(155 * 60),  # 2 hours 35 minutes in seconds
             calculate_parking_charge(155 * 60))  # ₹150 (₹50 + ₹50 + ₹50)
        ]

        # Add parking logs
        for log in user_logs:
            cur.execute("""
                INSERT INTO logs (rfid, in_time, out_time, duration, amount)
                VALUES (?, ?, ?, ?, ?)
            """, log)

        # Update user's amount based on paid logs
        cur.execute("""
            UPDATE user 
            SET amount = (
                SELECT COALESCE(SUM(amount), 0)
                FROM logs
                WHERE logs.rfid = user.rfid
            )
            WHERE rfid = '1'
        """)
        
        conn.commit()
        print("Sample data added successfully!")
    except Exception as e:
        print(f"Error adding sample data: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    add_sample_data() 