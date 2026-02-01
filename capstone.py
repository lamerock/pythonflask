from flask import Flask, render_template, request, url_for, flash, redirect, session, make_response
import sqlite3
from datetime import timedelta

app = Flask(__name__)

app.secret_key = '6c4f8cb5-be85-4d6e-b656-9905663d9bf4'
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
        _cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', 'admin123'))
        _cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('user', 'user123'))
        connection.commit()
    except sqlite3.IntegrityError:
        pass
    _cursor.close()
    connection.close()

## Verify user credentials ##
def verifyUser(username, password):
    connection = sqlite3.connect("database.db")
    _cursor = connection.cursor()
    _cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = _cursor.fetchone()
    _cursor.close()
    connection.close()
    return user is not None

## Get all inquiries from database ##
def getInquiries():
    connection = sqlite3.connect("database.db")
    _cursor = connection.cursor()
    _cursor.execute("SELECT * FROM inquiry")
    data = _cursor.fetchall()
    _cursor.close()
    connection.close()
    return data

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

@app.route("/")
def index():
    initDB()
    seedUsers()
    if 'user_logged_in' not in session:
        return render_template('landing.html')
    
    data = getInquiries()
    return render_template('dashboard.html', data=data)

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
    
    return render_template('inquiry-form.html')

@app.route('/add-record', methods=['POST'])
def add_record():
    name = request.form.get('txtName')
    email = request.form.get('txtEmail')
    inquiry_text = request.form.get('txtInquiry')
    
    if name and email and inquiry_text:
        if insertInquiry(name, email, inquiry_text):
            flash('Inquiry submitted successfully!', 'success')
            return render_template('success.html')
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
    data = getInquiries()
    return render_template('dashboard.html', data=data)

@app.route('/dashboard')
def dashboard():
    if 'user_logged_in' not in session:
        flash('Please log in to access the dashboard', 'warning')
        return redirect(url_for('index'))
    
    initDB()
    data = getInquiries()
    return render_template('dashboard.html', data=data)

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
    app.run(port=5001, debug=True)