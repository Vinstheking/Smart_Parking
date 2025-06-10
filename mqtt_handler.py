import paho.mqtt.client as mqtt
import sqlite3
from datetime import datetime
import math
import os
import time

# Ensure database directory exists
if not os.path.exists('database'):
    os.makedirs('database')

def get_db_connection():
    conn = sqlite3.connect('database/db.sqlite3')
    conn.row_factory = sqlite3.Row
    return conn

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

def on_connect(client, userdata, flags, reason_code, properties):
    print("Connected to MQTT broker")
    client.subscribe("parking/#")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    print(f"Received message: {topic} - {payload}")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        if topic == "parking/slots":
            # Handle slot updates
            slot_num, status = payload.split(":")
            # Validate slot number
            try:
                slot_num = int(slot_num)
                if slot_num < 1 or slot_num > 8:
                    print(f"Invalid slot number: {slot_num}. Valid slots are: 1-8")
                    return
            except ValueError:
                print(f"Invalid slot number format: {slot_num}")
                return
                
            cur.execute('''
                UPDATE slots 
                SET status = ? 
                WHERE slot_id = ?
            ''', (status, slot_num))
            print(f"Updated slot {slot_num} status to {status}")
            
        elif topic == "parking/rfid":
            # Handle RFID events
            if payload.startswith("entry:"):
                rfid = payload.split(":")[1]
                # Check if user exists
                cur.execute("SELECT * FROM user WHERE rfid = ?", (rfid,))
                user = cur.fetchone()
                cur.execute("SELECT COUNT(*) AS full_slots FROM slots WHERE status = 'occupied'")
                full_slots = cur.fetchone()['full_slots']
                total_slots = 8
                if full_slots == total_slots:
                    print("All slots are occupied. No entry allowed.")
                    client.publish("parking/gates/status", "entry:full")
                    return
                    
                elif user:
                    cur.execute('''
                        INSERT INTO logs (rfid, in_time, payment_status)
                        VALUES (?, datetime('now', 'localtime'), 'unpaid')
                    ''', (rfid,))
                    print(f"Created entry log for RFID: {rfid}")
                    # Publish gate open command
                    client.publish("parking/gates/status", "entry:open")
                else:
                    print(f"User with RFID {rfid} not found. Please register first.")
                    client.publish("parking/gates/status", "entry:unauthorized")
                    
            elif payload.startswith("exit:"):
                rfid = payload.split(":")[1]
                # Get the latest unpaid log
                cur.execute('''
                    SELECT * FROM logs 
                    WHERE rfid = ? AND payment_status = 'unpaid'
                    ORDER BY in_time DESC LIMIT 1
                ''', (rfid,))
                log = cur.fetchone()
                
                if log:
                    # Calculate duration and amount
                    entry_time = datetime.strptime(log['in_time'], "%Y-%m-%d %H:%M:%S")
                    exit_time = datetime.now()
                    duration_seconds = int((exit_time - entry_time).total_seconds())
                    amount = calculate_parking_charge(duration_seconds)
                    formatted_duration = format_duration(duration_seconds)
                    
                    cur.execute('''
                        UPDATE logs 
                        SET out_time = datetime('now', 'localtime'),
                            duration = ?,
                            amount = ?
                        WHERE id = ?
                    ''', (formatted_duration, amount, log['id']))
                    print(f"Updated exit log for RFID: {rfid}")
                    print(f"Duration: {formatted_duration}")
                    print(f"Amount: ₹{amount}")
                    # Publish gate open command
                    client.publish("parking/gates/status", "exit:open")
                else:
                    print(f"No active parking session found for RFID: {rfid}")
                    client.publish("parking/gates/status", "exit:unauthorized")
        
        conn.commit()
    except Exception as e:
        print(f"Error processing message: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

def on_disconnect(client, userdata, flags, reason_code, properties):
    print("Disconnected from MQTT broker")
    # Try to reconnect
    try:
        client.reconnect()
    except Exception as e:
        print(f"Reconnection failed: {str(e)}")

# Create MQTT client with MQTTv5
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

# Connect to broker
client.connect("192.168.154.42", 1883, 60)  # Using localhost

# Start the loop
client.loop_start()

print("MQTT Handler is running...")

try:
    while True:
        # Keep the script running
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopping MQTT Handler...")
    client.loop_stop()
    client.disconnect() 