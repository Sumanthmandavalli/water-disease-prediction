import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.neighbors import KNeighborsClassifier

# Load dataset
df = pd.read_csv("main_dataset.csv")

# Handle missing values
df.fillna(df.select_dtypes(include=[np.number]).mean(), inplace=True)
for col in df.select_dtypes(include=['object']).columns:
    df[col].fillna(df[col].mode()[0], inplace=True)

# Split 'Chemical Content Range (ppm)' into Min and Max values
df[['Min Chemical Content', 'Max Chemical Content']] = df['Chemical Content Range (ppm)'].str.split(' - ', expand=True).astype(float)
df.drop(columns=['Chemical Content Range (ppm)'], inplace=True)

# Encode categorical variables
label_encoders = {}
for col in ['Specific Contaminant', 'Related Disease(s)']:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le  

# Create a new feature (Difference in Chemical Content)
df['Chemical Content Diff'] = df['Max Chemical Content'] - df['Min Chemical Content']

# Define features and target variable
X = df[['Specific Contaminant', 'Min Chemical Content', 'Max Chemical Content', 'Chemical Content Diff']]
y = df['Related Disease(s)']

# Normalize features
scaler = StandardScaler()
X = scaler.fit_transform(X)

# Split into training/testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train KNN Classifier
knn = KNeighborsClassifier(n_neighbors=7, metric='euclidean')
knn.fit(X_train, y_train)

# Save model, scaler, and label encoder
with open("knn_model.pkl", "wb") as model_file:
    pickle.dump(knn, model_file)

with open("scaler.pkl", "wb") as scaler_file:
    pickle.dump(scaler, scaler_file)

with open("label_encoder.pkl", "wb") as le_file:
    pickle.dump(label_encoders['Related Disease(s)'], le_file)

print("Model saved successfully!")
