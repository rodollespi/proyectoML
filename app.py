from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps
import os
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import joblib

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

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
IMAGE_SIZE = (64, 64)

MODEL_PATH = os.path.join(app.root_path, 'models', 'modelo_flores_svm.pkl')
SCALER_PATH = os.path.join(app.root_path, 'models', 'scaler.pkl')
ENCODER_PATH = os.path.join(app.root_path, 'models', 'encoder.pkl')

modelo = joblib.load(MODEL_PATH)
escalador = joblib.load(SCALER_PATH)
codificador = joblib.load(ENCODER_PATH)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/clasificar_flor', methods=['GET'])
def index_1():
    return render_template('clasificar_flor.html')

@app.route('/clasificar', methods=['POST'])
def clasificar():
    if 'file' not in request.files:
        return render_template('clasificar_flor.html', error="No se envió ningún archivo.")
    file = request.files['file']
    if file.filename == '':
        return render_template('clasificar_flor.html', error="No se seleccionó archivo.")
    if not allowed_file(file.filename):
        return render_template('clasificar_flor.html', error="Extensión no permitida.")
    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(save_path)

    # Procesar imagen y predecir
    img = cv2.imread(save_path)
    if img is None:
        return render_template('clasificar_flor.html', error="No se pudo leer la imagen guardada.")
    img = cv2.resize(img, IMAGE_SIZE)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_flat = img.flatten().reshape(1, -1)
    img_scaled = escalador.transform(img_flat)

    pred = modelo.predict(img_scaled)[0]
    prob = modelo.predict_proba(img_scaled)[0]
    clase = codificador.inverse_transform([pred])[0]
    confianza = float(np.max(prob) * 100)

    return render_template('clasificar_flor.html',
                           filename=f'uploads/{filename}',
                           clase=clase,
                           confianza=f"{confianza:.2f}")




if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port) 