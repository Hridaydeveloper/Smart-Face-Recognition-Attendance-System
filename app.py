import os
import base64
import face_recognition
import numpy as np
import pandas as pd
import datetime
from flask import Flask, request, jsonify, render_template
from PIL import Image
from io import BytesIO
import shutil

app = Flask(__name__)

# Paths
FACE_DIR = 'known_faces'
EXCEL_FILE = 'attendance.xlsx'
os.makedirs(FACE_DIR, exist_ok=True)

# Store known encodings and names
known_encodings = []
known_names = []

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
            try:
                image = face_recognition.load_image_file(path)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    known_encodings.append(encodings[0])
                    known_names.append(name)
            except Exception as e:
                print(f"Error loading image {path}: {e}")

# Initial load
load_known_faces()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register-multiple', methods=['POST'])
def register_faces():
    data = request.get_json()
    name = data['name']
    images = data['images']

    for image_data in images:
        try:
            img_data = base64.b64decode(image_data.split(',')[1])
            img = Image.open(BytesIO(img_data)).convert('RGB')
            np_img = np.array(img)
            face_encodings = face_recognition.face_encodings(np_img)

            if not face_encodings:
                continue

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

    # Save images
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

                now = datetime.datetime.now()
                now_str = now.strftime('%Y-%m-%d %H:%M:%S')
                today = now.date()
                new_entry = pd.DataFrame([[name, now_str]], columns=["Name", "Timestamp"])

                if os.path.exists(EXCEL_FILE):
                    existing_df = pd.read_excel(EXCEL_FILE)
                    existing_df['Timestamp'] = pd.to_datetime(existing_df['Timestamp'])
                    already_marked = existing_df[
                        (existing_df["Name"] == name) &
                        (existing_df["Timestamp"].dt.date == today)
                    ]
                    if not already_marked.empty:
                        return jsonify({
                            "status": "duplicate",
                            "message": f"{name} is already marked present today."
                        })

                    updated_df = pd.concat([existing_df, new_entry], ignore_index=True)
                    updated_df.to_excel(EXCEL_FILE, index=False)
                else:
                    new_entry.to_excel(EXCEL_FILE, index=False)

                return jsonify({"status": "success", "message": f"Marked Present: {name}"})

        return jsonify({"status": "error", "message": "Face not recognized."})

    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to process image: {e}"})

@app.route('/list-users')
def list_users():
    users = [d for d in os.listdir(FACE_DIR) if os.path.isdir(os.path.join(FACE_DIR, d))]
    return jsonify({"users": users})

@app.route('/delete-user', methods=['POST'])
def delete_user():
    data = request.get_json()
    name = data.get("name")
    user_folder = os.path.join(FACE_DIR, name)

    if os.path.exists(user_folder):
        shutil.rmtree(user_folder)
        load_known_faces()
        return jsonify({"status": "success", "message": f"Deleted user: {name}"})
    else:
        return jsonify({"status": "error", "message": f"User not found: {name}"})


if __name__ == '__main__':
    app.run(debug=True)

