from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
import mysql.connector

app = Flask(__name__)
app.config['SECRET_KEY'] = 'please_amongbus'  # Replace with a strong secret key

def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='ecom'
    )
    return conn

@app.route('/')
def home():
    user_logged_in = 'username' in session
    user_initial = session['username'][0].upper() if user_logged_in else 'U'  # Default to 'U' if not logged in
    return render_template('homepage.html', user_logged_in=user_logged_in, user_initial=user_initial)

@app.route('/admin', methods=["GET"])
def admin():
    return render_template('admin_panel.html', show_register=True)

@app.route('/register', methods=['GET'])
def show_register():
    return render_template('register.html', show_register=True)

@app.route('/profile')
def show_profile():
    return render_template('profile.html')  # Create this template if it doesn't exist

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO accounts (username, email, password) VALUES (%s, %s, %s)', (username, email, password))
        conn.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('home'))
    except mysql.connector.IntegrityError:
        conn.rollback()
        flash('Email already exists. Try a different one.', 'error')
        return render_template('register.html', username=username, email=email, show_register=True)
    except Exception as e:
        conn.rollback()
        flash(f'An error occurred: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()

    return render_template('register.html', username=username, email=email, show_register=True)

@app.route('/login', methods=['POST'])
def login_user():
    email = request.form['email']
    password = request.form['password']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM accounts WHERE email = %s AND password = %s', (email, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        session['id'] = user['id']
        session['email'] = user['email']
        session['username'] = user['username']
        session['verification'] = user['verification']
        flash('Login successful!', 'success')  # Flash message for successful login
        
        if user['verification'] == 'nonverified':
            return redirect(url_for('home'))
        elif user['verification'] == 'verified':
            return redirect(url_for('home'))
        elif user['verification'] == 'admin':
            return redirect(url_for('admin'))
    else:
        flash('Invalid username or password. Please try again.', 'error')  # Flash message for failed login
        return render_template('register.html', show_register=False)  # Render the login page again

@app.route('/redirectlogin', methods=['GET'])
def redirectlogin():
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/api/fetch_user_accounts/', methods=['GET'])
def fetch_user_accounts():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, username, email, verification FROM accounts')
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users)

if __name__ == '__main__':
    app.run(debug=True)