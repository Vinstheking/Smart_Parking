from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime
import math
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Ensure database directory exists
if not os.path.exists('database'):
    os.makedirs('database')

def init_db():
    conn = sqlite3.connect('database/db.sqlite3')
    cur = conn.cursor()
    
    # Create tables if they don't exist
    cur.execute('''
        CREATE TABLE IF NOT EXISTS user (
            rfid TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS logs (
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
    
    # Add payment_status column if it doesn't exist
    try:
        cur.execute("ALTER TABLE logs ADD COLUMN payment_status TEXT DEFAULT 'unpaid'")
    except sqlite3.OperationalError:
        # Column already exists
        pass
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS slots (
            slot_id INTEGER PRIMARY KEY,
            status TEXT DEFAULT 'free'
        )
    ''')
    
    # Create 8 slots if they don't exist
    for i in range(1, 9):
        cur.execute('INSERT OR IGNORE INTO slots (slot_id, status) VALUES (?, ?)', (i, 'free'))
    
    # Clean up owner parking logs
    cur.execute("""
        DELETE FROM logs 
        WHERE rfid IN (SELECT rfid FROM user WHERE role = 'owner')
    """)
    
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        rfid = request.form['rfid']
        role = request.form['role']

        conn = sqlite3.connect('database/db.sqlite3')
        cur = conn.cursor()
        cur.execute("SELECT * FROM user WHERE rfid=? AND role=?", (rfid, role))
        user = cur.fetchone()
        conn.close()

        if user:
            session['rfid'] = user[0]
            session['role'] = user[2]
            session['name'] = user[1]
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid RFID or Role', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'role' not in session:
        return redirect(url_for('login'))

    rfid = session['rfid']
    role = session['role']
    name = session.get('name', '')

    conn = sqlite3.connect('database/db.sqlite3')
    cur = conn.cursor()

    # Get all slots for both views
    cur.execute("SELECT * FROM slots ORDER BY slot_id")
    all_slots = cur.fetchall()

    # Get all logs for both views
    cur.execute('''
        SELECT logs.id, logs.rfid, user.name, logs.in_time, logs.out_time, 
               logs.duration, logs.amount, COALESCE(logs.payment_status, 'unpaid') as payment_status
        FROM logs 
        LEFT JOIN user ON logs.rfid = user.rfid
        ORDER BY logs.in_time DESC
    ''')
    all_logs = cur.fetchall()

    # Get all users for owner view
    cur.execute("SELECT * FROM user")
    all_users = cur.fetchall()

    # Prepare user-specific data
    cur.execute("""
        SELECT id, rfid, in_time, out_time, duration, amount, 
               COALESCE(payment_status, 'unpaid') as payment_status
        FROM logs 
        WHERE rfid = ? 
        ORDER BY in_time DESC
    """, (rfid,))
    user_logs = cur.fetchall()
    
    paid_logs = []
    unpaid_logs = []

    for log in user_logs:
        in_time = log[2]
        out_time = log[3]

        if in_time and out_time:
            in_dt = datetime.strptime(in_time, "%Y-%m-%d %H:%M:%S")
            out_dt = datetime.strptime(out_time, "%Y-%m-%d %H:%M:%S")
            duration = out_dt - in_dt
            hours = int(duration.total_seconds() // 3600)
            minutes = int((duration.total_seconds() % 3600) // 60)
            duration_str = f"{hours} hr {minutes} min" if hours > 0 else f"{minutes} min"
            calculated_amount = calculate_parking_charge(duration.total_seconds() / 3600)
        else:
            duration_str = 'N/A'
            calculated_amount = 0

        # Get payment status
        payment_status = log[6]  # payment_status is at index 6

        log_dict = {
            'id': log[0],
            'in_time': in_time,
            'out_time': out_time if out_time else 'N/A',
            'duration': duration_str,
            'status': payment_status,
            'amount': calculated_amount
        }

        if payment_status == 'paid':
            paid_logs.append(log_dict)
        else:
            unpaid_logs.append(log_dict)

    total = sum(log['amount'] for log in paid_logs)
    conn.close()

    return render_template(
        'dashboard.html',
        name=name,
        role=role,
        all_slots=all_slots,
        all_logs=all_logs,
        all_users=all_users,
        user_logs=unpaid_logs,
        paid_logs=paid_logs,
        total=total
    )

def calculate_parking_charge(hours):
    # First hour or part thereof: ₹50
    # Each additional hour or part thereof: ₹50
    if hours <= 1:
        return 50
    else:
        return 50 + (math.ceil(hours - 1) * 50)

@app.route('/rfid_auth', methods=['POST'])
def rfid_auth():
    rfid = request.form.get('rfid')
    gate = request.form.get('gate')
    
    conn = sqlite3.connect('database/db.sqlite3')
    cur = conn.cursor()
    
    # Check if RFID exists in database and get user role
    cur.execute("SELECT role FROM user WHERE rfid = ?", (rfid,))
    result = cur.fetchone()
    
    if result:
        role = result[0]
        if role == 'owner':
            flash('Owner RFID cards cannot be used for parking', 'error')
            conn.close()
            return jsonify({'status': 'error', 'message': 'Owner RFID cards cannot be used for parking'})
        
        if gate == 'entry':
            # Create new parking log
            cur.execute('''
                INSERT INTO logs (rfid, in_time, out_time, duration, amount)
                VALUES (?, datetime('now'), NULL, NULL, NULL)
            ''', (rfid,))
            conn.commit()
            flash('Entry recorded successfully', 'success')
        else:  # exit
            # Update existing log
            cur.execute('''
                SELECT id, in_time FROM logs 
                WHERE rfid = ? AND out_time IS NULL 
                ORDER BY in_time DESC LIMIT 1
            ''', (rfid,))
            log = cur.fetchone()
            
            if log:
                log_id, in_time = log
                in_dt = datetime.strptime(in_time, "%Y-%m-%d %H:%M:%S")
                out_dt = datetime.now()
                duration = out_dt - in_dt
                hours = duration.total_seconds() / 3600
                amount = calculate_parking_charge(hours)
                
                cur.execute('''
                    UPDATE logs 
                    SET out_time = datetime('now'),
                        duration = ?,
                        amount = ?
                    WHERE id = ?
                ''', (str(duration), amount, log_id))
                conn.commit()
                flash('Exit recorded successfully', 'success')
            else:
                flash('No active parking session found', 'error')
    else:
        flash('Invalid RFID card', 'error')
    
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/update_slot_status', methods=['POST'])
def update_slot_status():
    slot_id = request.form.get('slot_id')
    status = request.form.get('status')
    
    conn = sqlite3.connect('database/db.sqlite3')
    cur = conn.cursor()
    
    try:
        cur.execute('''
            UPDATE slots 
            SET status = ? 
            WHERE slot_id = ?
        ''', (status, slot_id))
        
        conn.commit()
        flash(f'Slot {slot_id} status updated successfully', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error updating slot status: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('dashboard'))

@app.route('/pay/<int:log_id>')
def pay(log_id):
    if 'role' not in session or session['role'] != 'user':
        return redirect(url_for('login'))

    conn = sqlite3.connect('database/db.sqlite3')
    cur = conn.cursor()
    
    try:
        # Get log details
        cur.execute("SELECT in_time, out_time FROM logs WHERE id = ? AND rfid = ?", (log_id, session['rfid']))
        row = cur.fetchone()
        
        if row and row[0] and row[1]:
            in_dt = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
            out_dt = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
            hours = (out_dt - in_dt).total_seconds() / 3600
            amount = calculate_parking_charge(hours)
            
            # Update log with payment and payment status
            cur.execute("""
                UPDATE logs 
                SET amount = ?, 
                    payment_status = 'paid' 
                WHERE id = ? AND rfid = ?
            """, (amount, log_id, session['rfid']))
            conn.commit()
            flash('Payment successful', 'success')
        else:
            flash('Invalid log entry', 'error')
    except Exception as e:
        conn.rollback()
        flash(f'Error processing payment: {str(e)}', 'error')
    finally:
        conn.close()

    return redirect(url_for('dashboard'))

@app.route('/update_user', methods=['POST'])
def update_user():
    if 'role' not in session or session['role'] != 'owner':
        return redirect(url_for('login'))

    rfid = request.form['rfid']
    name = request.form['name']
    role = request.form['role']

    conn = sqlite3.connect('database/db.sqlite3')
    cur = conn.cursor()
    
    try:
        cur.execute("UPDATE user SET name = ?, role = ? WHERE rfid = ?", (name, role, rfid))
        conn.commit()
        flash('User updated successfully', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error updating user: {str(e)}', 'error')
    finally:
        conn.close()

    return redirect(url_for('dashboard'))

@app.route('/add_user', methods=['POST'])
def add_user():
    if 'role' not in session or session['role'] != 'owner':
        return redirect(url_for('login'))

    rfid = request.form['rfid']
    name = request.form['name']
    role = request.form['role']

    conn = sqlite3.connect('database/db.sqlite3')
    cur = conn.cursor()
    
    try:
        cur.execute("INSERT INTO user (rfid, name, role) VALUES (?, ?, ?)", (rfid, name, role))
        conn.commit()
        flash('User added successfully', 'success')
    except sqlite3.IntegrityError:
        conn.rollback()
        flash('RFID already exists', 'error')
    except Exception as e:
        conn.rollback()
        flash(f'Error adding user: {str(e)}', 'error')
    finally:
        conn.close()

    return redirect(url_for('dashboard'))

@app.route('/delete_user/<rfid>')
def delete_user(rfid):
    if 'role' not in session or session['role'] != 'owner':
        return redirect(url_for('login'))

    conn = sqlite3.connect('database/db.sqlite3')
    cur = conn.cursor()
    
    try:
        # First delete all logs associated with the user
        cur.execute("DELETE FROM logs WHERE rfid = ?", (rfid,))
        # Then delete the user
        cur.execute("DELETE FROM user WHERE rfid = ?", (rfid,))
        conn.commit()
        flash('User and associated logs deleted successfully', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting user: {str(e)}', 'error')
    finally:
        conn.close()

    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
