from flask import Flask, request, jsonify, render_template
import numpy as np
import pickle
import sqlite3
from sklearn.preprocessing import StandardScaler
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define Database Model for Storing Predictions
class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    water_source = db.Column(db.String(100))
    contaminant_type = db.Column(db.String(100))
    specific_contaminant = db.Column(db.String(100))
    min_chem = db.Column(db.Float)
    max_chem = db.Column(db.Float)
    chemical_diff = db.Column(db.Float)
    predicted_disease = db.Column(db.String(100))

# Create tables in the database
with app.app_context():
    db.create_all()

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
@app.route('/predictions')
def predictions():
    return render_template('predictions.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    try:
        patient_name = data.get('patient_name', "Unknown")
        age = int(data.get('age', 0))
        gender = data.get('gender', "Unknown")
        specific_contaminant = data.get('specific_contaminant', "").strip()
        contaminant_type = data.get('contaminant_type', "Unknown")
        min_chem = float(data.get('min_chemical', 0))
        max_chem = float(data.get('max_chemical', 0))
        water_source = data.get('water_source', "Unknown")
        chemical_diff = max_chem - min_chem

        contaminant_dict = {
            "Arsenic": 1, "Chlorine (Disinfection By-products)": 2, "Cryptosporidium": 3,
            "Dracunculus medinensis": 4, "Escherichia coli": 5, "Giardia lamblia": 6,
            "Hepatitis A Virus (HAV)": 7, "Lead": 8, "Leptospira": 9, "Microplastics": 10,
            "Nitrates": 11, "Poliovirus": 12, "Radon": 13, "Salmonella typhi": 14,
            "Schistosoma": 15, "Sediments (Silt, Organic Debris)": 16, "Shigella": 17,
            "Vibrio cholerae": 18
        }

        if specific_contaminant in contaminant_dict:
            specific_contaminant_encoded = contaminant_dict[specific_contaminant]
        else:
            return jsonify({"error": f"Unknown contaminant: {specific_contaminant}"}), 400

        input_data = np.array([[specific_contaminant_encoded, min_chem, max_chem, chemical_diff]])
        input_data_scaled = scaler.transform(input_data)
        pred = knn.predict(input_data_scaled)
        predicted_disease = label_encoder.inverse_transform([int(pred[0])])[0]

        new_prediction = Prediction(
            patient_name=patient_name,
            age=age,
            gender=gender,
            water_source=water_source,
            contaminant_type=contaminant_type,
            specific_contaminant=specific_contaminant,
            min_chem=min_chem,
            max_chem=max_chem,
            chemical_diff=chemical_diff,
            predicted_disease=predicted_disease
        )

        db.session.add(new_prediction)
        db.session.commit()
        
        print("Data successfully stored in the database:", new_prediction)

        return jsonify({
            'patient_name': patient_name,
            'age': age,
            'gender': gender,
            'water_source': water_source,
            'contaminant_type': contaminant_type,
            'predicted_disease': predicted_disease
        })

    except Exception as e:
        db.session.rollback()
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/get_predictions', methods=['GET'])
def get_predictions():
    try:
        predictions = Prediction.query.all()
        if not predictions:
            return jsonify([]), 200  

        results = [{
            'id': p.id,
            'patient_name': p.patient_name,
            'age': p.age,
            'gender': p.gender,
            'water_source': p.water_source,
            'contaminant_type': p.contaminant_type,
            'specific_contaminant': p.specific_contaminant,
            'min_chem': p.min_chem,
            'max_chem': p.max_chem,
            'chemical_diff': p.chemical_diff,
            'predicted_disease': p.predicted_disease
        } for p in predictions]

        print("✅ Fetched predictions:", results)  # Debugging

        return jsonify(results), 200

    except Exception as e:
        print("❌ Error fetching predictions:", str(e))  
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
