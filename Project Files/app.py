from flask import Flask, render_template, request
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Load the model
model = load_model('healthy_vs_rotten.h5')

# Upload folder
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Class labels (based on your trained model)
class_names = ['Healthy', 'Newcastle', 'Salmonella', 'Bronchitis']  # adjust if needed

# Disease details dictionary
disease_info = {
    "Healthy": {
        "symptoms": "No symptoms. Bird is healthy.",
        "medicine": "No medicine needed."
    },
    "Newcastle": {
        "symptoms": "Coughing, sneezing, greenish diarrhea, paralysis, twisted neck.",
        "medicine": "Vaccination (Lasota or B1), supportive multivitamins."
    },
    "Salmonella": {
        "symptoms": "Diarrhea, dehydration, weakness, reduced egg production.",
        "medicine": "Antibiotics (e.g., Enrofloxacin, Sulfa drugs). Maintain hygiene."
    },
    "Bronchitis": {
        "symptoms": "Nasal discharge, sneezing, gasping, drop in egg quality.",
        "medicine": "Use IB vaccine. Give electrolytes and vitamins for support."
    }
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/output', methods=['POST'])
def output():
    if 'file' not in request.files:
        return "No file uploaded", 400

    file = request.files['file']

    if file.filename == '':
        return "No selected file", 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Preprocess image
    img = image.load_img(filepath, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0

    # Prediction
    prediction = model.predict(img_array)
    predicted_class = class_names[np.argmax(prediction)]

    # Get info
    symptoms = disease_info[predicted_class]["symptoms"]
    medicine = disease_info[predicted_class]["medicine"]

    return render_template(
        'index.html',
        result=predicted_class,
        img_path=filepath,
        symptoms=symptoms,
        medicine=medicine
    )

if __name__ == '__main__':
    app.run(debug=True)
