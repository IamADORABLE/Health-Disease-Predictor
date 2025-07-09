from flask import Flask, request, render_template
import joblib
import pandas as pd
import os

app = Flask(__name__)

# === Safe loading of model and data ===
def safe_load_files():
    try:
        print("📦 Loading model and encoders...")
        model = joblib.load("naive_bayes_model.pkl")
        le = joblib.load("label_encoder.pkl")
        all_symptoms = joblib.load("symptom_features.pkl")
        print("✅ Model and encoders loaded successfully.")
    except Exception as e:
        print("❌ MODEL LOAD ERROR:", e)
        raise e

    try:
        print("📦 Loading data CSVs...")
        description_df = pd.read_csv("description.csv")
        medications_df = pd.read_csv("medications.csv")
        diets_df = pd.read_csv("diets.csv")
        precautions_df = pd.read_csv("precautions_df.csv")
        workouts_df = pd.read_csv("workout_df.csv")
        print("✅ CSV files loaded successfully.")
    except Exception as e:
        print("❌ CSV LOAD ERROR:", e)
        raise e

    return model, le, all_symptoms, description_df, medications_df, diets_df, precautions_df, workouts_df

# Load everything
model, le, all_symptoms, description_df, medications_df, diets_df, precautions_df, workouts_df = safe_load_files()

# === Normalize and clean ===
description_df.columns = description_df.columns.str.strip()
medications_df.columns = medications_df.columns.str.strip()
diets_df.columns = diets_df.columns.str.strip()
precautions_df.columns = precautions_df.columns.str.strip()
workouts_df.columns = workouts_df.columns.str.strip()

all_symptoms = [s.strip().lower() for s in all_symptoms if pd.notna(s)]
workouts_df.rename(columns={"disease": "Disease", "workout": "Workout"}, inplace=True)

# === Disease info fetcher ===
def get_disease_info(disease):
    disease_lower = disease.lower()

    description = description_df.loc[description_df['Disease'].str.lower() == disease_lower, 'Description'].values
    medication = medications_df.loc[medications_df['Disease'].str.lower() == disease_lower, 'Medication'].values
    diet = diets_df.loc[diets_df['Disease'].str.lower() == disease_lower, 'Diet'].values

    precaution_row = precautions_df[precautions_df['Disease'].str.lower() == disease_lower]
    if not precaution_row.empty:
        precaution_values = precaution_row[['Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4']].values[0]
        precaution = ", ".join([p for p in precaution_values if pd.notna(p)])
    else:
        precaution = "Not available"

    workout = workouts_df.loc[workouts_df['Disease'].str.lower() == disease_lower, 'Workout'].values

    return {
        "description": description[0] if len(description) else "Not available",
        "medication": medication[0] if len(medication) else "Not available",
        "diet": diet[0] if len(diet) else "Not available",
        "precautions": precaution,
        "workout": workout[0] if len(workout) else "Not available"
    }

# === Routes ===
@app.route('/')
def home():
    return render_template('index.html', all_symptoms=all_symptoms)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        with open('messages.txt', 'a', encoding='utf-8') as f:
            f.write(f"Name: {name}\nEmail: {email}\nMessage: {message}\n---\n")

        return render_template('contact.html', success=True)
    return render_template('contact.html')

@app.route('/predict', methods=['POST'])
def predict():
    symptoms = request.form['symptoms']
    symptoms_list = [s.strip().lower() for s in symptoms.split(',')]

    input_vector = [1 if symptom in symptoms_list else 0 for symptom in all_symptoms]

    try:
        prediction_num = model.predict([input_vector])[0]
        prediction = le.inverse_transform([prediction_num])[0]
        disease_info = get_disease_info(prediction)
    except Exception as e:
        print("❌ PREDICTION ERROR:", e)
        return render_template('index.html', all_symptoms=all_symptoms, prediction_text="Error during prediction.")

    return render_template(
        'index.html',
        prediction_text=f"Predicted disease: {prediction}",
        all_symptoms=all_symptoms,
        disease_info=disease_info
    )

# === Start app for local dev ===
if __name__ == '__main__':
    print("📂 Current directory:", os.getcwd())
    print("📁 Files in directory:", os.listdir())
    app.run(debug=True)
