import os
import numpy as np
import cv2
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report
import joblib


base_dir = 'Images/'
image_size = (64, 64) 


X = []
y = []

for folder in os.listdir(base_dir):
    folder_path = os.path.join(base_dir, folder)
    if not os.path.isdir(folder_path):
        continue
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            img = cv2.imread(file_path)
            img = cv2.resize(img, image_size)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            X.append(img.flatten())
            y.append(folder)

X = np.array(X)
y = np.array(y)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y_encoded, test_size=0.2, random_state=42
)

model = SVC(kernel='linear', probability=True, random_state=42)
model.fit(X_train, y_train)


y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)


os.makedirs('models', exist_ok=True)
joblib.dump(model, 'models/modelo_flores_svm.pkl')
joblib.dump(scaler, 'models/scaler.pkl')
joblib.dump(encoder, 'models/encoder.pkl')

def clasificar_imagen(ruta):
    if not os.path.exists(ruta):
        print(f"No se encontró la imagen {ruta}")
        return
    img = cv2.imread(ruta)
    img = cv2.resize(img, image_size)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_flat = img.flatten().reshape(1, -1)
    img_scaled = scaler.transform(img_flat)
    pred = model.predict(img_scaled)[0]
    prob = model.predict_proba(img_scaled)[0]
    clase = encoder.inverse_transform([pred])[0]
    confianza = np.max(prob) * 100
    print(f"\n La imagen '{ruta}' pertenece a la clase '{clase}")
    