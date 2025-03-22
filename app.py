from flask import Flask, request, jsonify, render_template
import numpy as np
import pickle
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)

# Load trained KNN model and scaler
with open("knn_model.pkl", "rb") as model_file:
    knn = pickle.load(model_file)

with open("scaler.pkl", "rb") as scaler_file:
    scaler = pickle.load(scaler_file)

# Load label encoder for disease decoding
with open("label_encoder.pkl", "rb") as le_file:
    label_encoder = pickle.load(le_file)

@app.route('/')
def home():
    return render_template('home.html')  

@app.route('/treated_water')
def treated_water():
    return render_template('treated_water.html')

@app.route('/natural_water')
def natural_water():
    return render_template('natural_water.html')

@app.route('/managed_water')
def managed_water():
    return render_template('managed_water.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json

    patient_name = data['patient_name']
    age = int(data['age'])
    gender = data['gender']
    specific_contaminant = float(data['specific_contaminant'])
    min_chem = float(data['min_chemical'])
    max_chem = float(data['max_chemical'])
    water_source = data['water_source']
    chemical_diff = max_chem - min_chem
    input_data = np.array([[specific_contaminant, min_chem, max_chem, chemical_diff]])
    input_data_scaled = scaler.transform(input_data)
    pred = knn.predict(input_data_scaled)
    predicted_disease = label_encoder.inverse_transform([int(pred[0])])[0]

    return jsonify({'patient_name': patient_name, 'age': age, 'gender': gender, 'water_source': water_source, 'predicted_disease': predicted_disease})

if __name__ == '__main__':
    app.run(debug=True)
