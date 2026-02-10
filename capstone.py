from flask import Flask, render_template, request, url_for, flash, redirect, session, make_response
import sqlite3
from datetime import timedelta
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
app.permanent_session_lifetime = timedelta(minutes=30)

## Init Database Tables ##
def initDB():
    connection = sqlite3.connect("database.db")
    _cursor = connection.cursor()
    _cursor.execute("CREATE TABLE IF NOT EXISTS inquiry (id integer primary key autoincrement, name text, email text, inquiry text)")
    _cursor.execute("CREATE TABLE IF NOT EXISTS users (id integer primary key autoincrement, username text unique, password text)")
    _cursor.close()
    connection.commit()
    connection.close()

## Seed admin users ##
def seedUsers():
    connection = sqlite3.connect("database.db")
    _cursor = connection.cursor()
    try:
        admin_hash = generate_password_hash('admin123')
        user_hash = generate_password_hash('user123')
        _cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', admin_hash))
        _cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('user', user_hash))
        connection.commit()
    except sqlite3.IntegrityError:
        pass
    _cursor.close()
    connection.close()

## Verify user credentials ##
def verifyUser(username, password):
    connection = sqlite3.connect("database.db")
    _cursor = connection.cursor()
    _cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = _cursor.fetchone()
    _cursor.close()
    connection.close()
    if result:
        stored_hash = result[0]
        return check_password_hash(stored_hash, password)
    return False

## Get all inquiries from database ##
def getInquiries():
    # legacy: return all inquiries
    connection = sqlite3.connect("database.db")
    _cursor = connection.cursor()
    _cursor.execute("SELECT * FROM inquiry")
    data = _cursor.fetchall()
    _cursor.close()
    connection.close()
    return data


def getInquiriesFiltered(search=None, page=None, per_page=None):
    connection = sqlite3.connect("database.db")
    _cursor = connection.cursor()

    params = []
    where_clause = ""
    if search:
        where_clause = "WHERE name LIKE ? OR email LIKE ? OR inquiry LIKE ?"
        like = f"%{search}%"
        params.extend([like, like, like])

    # total count
    count_query = f"SELECT COUNT(*) FROM inquiry {where_clause}"
    _cursor.execute(count_query, params)
    total = _cursor.fetchone()[0]

    # if pagination not requested, return all
    if not page or not per_page:
        query = f"SELECT * FROM inquiry {where_clause} ORDER BY id DESC"
        _cursor.execute(query, params)
        data = _cursor.fetchall()
        _cursor.close()
        connection.close()
        return data, total

    offset = (page - 1) * per_page
    query = f"SELECT * FROM inquiry {where_clause} ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([per_page, offset])
    _cursor.execute(query, params)
    data = _cursor.fetchall()
    _cursor.close()
    connection.close()
    return data, total

## Insert inquiry into database ##
def insertInquiry(name, email, inquiry):
    try:
        connection = sqlite3.connect("database.db")
        _cursor = connection.cursor()
        _cursor.execute("INSERT INTO inquiry (name, email, inquiry) VALUES (?, ?, ?)", (name, email, inquiry))
        _cursor.close()
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"Error inserting inquiry: {e}")
        return False


def getInquiryById(inquiry_id):
    connection = sqlite3.connect("database.db")
    _cursor = connection.cursor()
    _cursor.execute("SELECT * FROM inquiry WHERE id = ?", (inquiry_id,))
    row = _cursor.fetchone()
    _cursor.close()
    connection.close()
    return row


def updateInquiry(inquiry_id, name, email, inquiry_text):
    try:
        connection = sqlite3.connect("database.db")
        _cursor = connection.cursor()
        _cursor.execute("UPDATE inquiry SET name = ?, email = ?, inquiry = ? WHERE id = ?",
                        (name, email, inquiry_text, inquiry_id))
        connection.commit()
        _cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f"Error updating inquiry: {e}")
        return False


def deleteInquiry(inquiry_id):
    try:
        connection = sqlite3.connect("database.db")
        _cursor = connection.cursor()
        _cursor.execute("DELETE FROM inquiry WHERE id = ?", (inquiry_id,))
        connection.commit()
        _cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f"Error deleting inquiry: {e}")
        return False

@app.route("/")
def index():
    initDB()
    seedUsers()
    if 'user_logged_in' not in session:
        return render_template('landing.html')
    # show paginated inquiries on index for logged-in users
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    q = request.args.get('q', None)
    data, total = getInquiriesFiltered(search=q, page=page, per_page=per_page)
    total_pages = (total + per_page - 1) // per_page if per_page else 1
    return render_template('dashboard.html', data=data, page=page, per_page=per_page, total=total, total_pages=total_pages, q=q)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/inquiry', methods=['GET', 'POST'])
def inquiry():
    if request.method == 'POST':
        name = request.form.get('txtName')
        email = request.form.get('txtEmail')
        inquiry_text = request.form.get('txtInquiry')
        
        if name and email and inquiry_text:
            if insertInquiry(name, email, inquiry_text):
                flash('Inquiry submitted successfully!', 'success')
                return redirect(url_for('inquiry'))
            else:
                flash('Error submitting inquiry. Please try again.', 'danger')
        else:
            flash('Please fill in all fields!', 'danger')
    
    return render_template('inquiry-form.html', action_url=url_for('add_record'), submit_label='Submit')

@app.route('/add-record', methods=['POST'])
def add_record():
    name = request.form.get('txtName')
    email = request.form.get('txtEmail')
    inquiry_text = request.form.get('txtInquiry')
    
    if name and email and inquiry_text:
        if insertInquiry(name, email, inquiry_text):
            flash('Inquiry submitted successfully!', 'success')
            return redirect(url_for('inquiry'))
        else:
            flash('Error submitting inquiry. Please try again.', 'danger')
            return render_template('failed.html')
    else:
        flash('Please fill in all fields!', 'danger')
        return render_template('failed.html')

@app.route('/display')
def display():
    if 'user_logged_in' not in session:
        flash('Please log in to access the dashboard', 'warning')
        return redirect(url_for('index'))
    initDB()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    q = request.args.get('q', None)
    data, total = getInquiriesFiltered(search=q, page=page, per_page=per_page)
    total_pages = (total + per_page - 1) // per_page if per_page else 1
    return render_template('dashboard.html', data=data, page=page, per_page=per_page, total=total, total_pages=total_pages, q=q)

@app.route('/dashboard')
def dashboard():
    if 'user_logged_in' not in session:
        flash('Please log in to access the dashboard', 'warning')
        return redirect(url_for('index'))
    initDB()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    q = request.args.get('q', None)
    data, total = getInquiriesFiltered(search=q, page=page, per_page=per_page)
    total_pages = (total + per_page - 1) // per_page if per_page else 1
    return render_template('dashboard.html', data=data, page=page, per_page=per_page, total=total, total_pages=total_pages, q=q)


@app.route('/inquiry/<int:inquiry_id>/edit', methods=['GET'])
def edit_inquiry(inquiry_id):
    if 'user_logged_in' not in session:
        flash('Please log in to access this page', 'warning')
        return redirect(url_for('index'))
    initDB()
    row = getInquiryById(inquiry_id)
    if not row:
        flash('Inquiry not found', 'danger')
        return redirect(url_for('dashboard'))
    # row: (id, name, email, inquiry)
    return render_template('inquiry-form.html', action_url=url_for('update_inquiry', inquiry_id=inquiry_id), submit_label='Update', name_value=row[1], email_value=row[2], inquiry_value=row[3])


@app.route('/update/<int:inquiry_id>', methods=['POST'])
def update_inquiry(inquiry_id):
    if 'user_logged_in' not in session:
        flash('Please log in to access this page', 'warning')
        return redirect(url_for('index'))
    name = request.form.get('txtName')
    email = request.form.get('txtEmail')
    inquiry_text = request.form.get('txtInquiry')
    if not (name and email and inquiry_text):
        flash('Please fill in all fields!', 'danger')
        return redirect(url_for('edit_inquiry', inquiry_id=inquiry_id))
    if updateInquiry(inquiry_id, name, email, inquiry_text):
        flash('Inquiry updated successfully!', 'success')
    else:
        flash('Error updating inquiry.', 'danger')
    return redirect(url_for('dashboard'))


@app.route('/delete/<int:inquiry_id>', methods=['POST'])
def delete_inquiry(inquiry_id):
    if 'user_logged_in' not in session:
        flash('Please log in to access this action', 'warning')
        return redirect(url_for('index'))
    if deleteInquiry(inquiry_id):
        flash('Inquiry deleted.', 'info')
    else:
        flash('Error deleting inquiry.', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username and password:
            if verifyUser(username, password):
                session.permanent = True
                session['user_logged_in'] = True
                session['username'] = username
                flash('Access granted. Welcome back, ' + username, 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid credentials. Access denied.', 'danger')
        else:
            flash('Please fill in all fields!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Session terminated. Goodbye.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Use PORT env var from cloud platforms (Render, Railway, etc.), default to 5001 for local dev
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)