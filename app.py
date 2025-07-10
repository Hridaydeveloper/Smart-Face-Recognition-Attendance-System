import os
import base64
import face_recognition
import numpy as np
import pandas as pd
import datetime
from flask import Flask, request, jsonify, render_template
from PIL import Image
from io import BytesIO

app = Flask(__name__)

# Paths
FACE_DIR = 'known_faces'
EXCEL_FILE = 'attendance.xlsx'
os.makedirs(FACE_DIR, exist_ok=True)

# Store known encodings and names
known_encodings = []
known_names = []

# Load all stored faces into memory
def load_known_faces():
    global known_encodings, known_names
    known_encodings = []
    known_names = []

    for name in os.listdir(FACE_DIR):
        user_dir = os.path.join(FACE_DIR, name)
        if not os.path.isdir(user_dir):
            continue

        for img_file in os.listdir(user_dir):
            path = os.path.join(user_dir, img_file)
            image = face_recognition.load_image_file(path)
            encodings = face_recognition.face_encodings(image)

            if encodings:
                known_encodings.append(encodings[0])
                known_names.append(name)

# Load faces on start
load_known_faces()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# Register user with multiple images (with duplicate face check)
@app.route('/register-multiple', methods=['POST'])
def register_faces():
    data = request.get_json()
    name = data['name']
    images = data['images']

    # Step 1: Check for duplicate face
    for image_data in images:
        try:
            img_data = base64.b64decode(image_data.split(',')[1])
            img = Image.open(BytesIO(img_data)).convert('RGB')
            np_img = np.array(img)
            face_encodings = face_recognition.face_encodings(np_img)

            if not face_encodings:
                continue  # No face detected

            new_encoding = face_encodings[0]
            matches = face_recognition.compare_faces(known_encodings, new_encoding, tolerance=0.45)

            if True in matches:
                match_index = matches.index(True)
                matched_name = known_names[match_index]
                return jsonify({
                    "status": "error",
                    "message": f"This face is already registered as: {matched_name}"
                })

        except Exception as e:
            return jsonify({"status": "error", "message": f"Image check failed: {e}"})

    # Step 2: Save new images
    user_folder = os.path.join(FACE_DIR, name)
    os.makedirs(user_folder, exist_ok=True)

    for i, image_data in enumerate(images):
        try:
            img_data = base64.b64decode(image_data.split(',')[1])
            img = Image.open(BytesIO(img_data)).convert('RGB')
            img_path = os.path.join(user_folder, f"{i}.jpg")
            img.save(img_path)
        except Exception as e:
            return jsonify({"status": "error", "message": f"Failed to save image {i}: {e}"})

    load_known_faces()
    return jsonify({"status": "success", "message": f"{name} registered successfully."})

# Start attendance
@app.route('/start-attendance', methods=['POST'])
def mark_attendance():
    data = request.get_json()
    image_data = data['image']

    try:
        img_data = base64.b64decode(image_data.split(',')[1])
        img = Image.open(BytesIO(img_data)).convert('RGB')
        frame = np.array(img)

        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        if not face_encodings:
            return jsonify({"status": "error", "message": "No face detected."})

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.45)
            name = "Unknown"

            if True in matches:
                first_match_index = matches.index(True)
                name = known_names[first_match_index]

                now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                df = pd.DataFrame([[name, now]], columns=["Name", "Timestamp"])

                if os.path.exists(EXCEL_FILE):
                    existing_df = pd.read_excel(EXCEL_FILE)
                    combined_df = pd.concat([existing_df, df], ignore_index=True)
                    combined_df.to_excel(EXCEL_FILE, index=False)
                else:
                    df.to_excel(EXCEL_FILE, index=False)

                return jsonify({"status": "success", "message": f"Marked Present: {name}"})

        return jsonify({"status": "error", "message": "Face not recognized."})

    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to process image: {e}"})

@app.route('/list-users')
def list_users():
    users = [d for d in os.listdir(FACE_DIR) if os.path.isdir(os.path.join(FACE_DIR, d))]
    return jsonify({"users": users})

if __name__ == '__main__':
    load_known_faces()
    app.run(debug=True)
