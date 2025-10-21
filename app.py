from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = '12356789'


USERNAME = 'root'
PASSWORD = 'password'


  
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            error = 'datos no validos'
    
    return render_template('login.html', error=error)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=session.get('username'))

@app.route('/entendimiento')
@login_required
def entendimiento():
    return render_template('entendimiento.html')

@app.route('/ingenieriaDeDatos')
@login_required
def ingenieriaDeDatos():
    return render_template('ingenieriaDeDatos.html')



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port