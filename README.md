#Smart Face Recognition Attendance System

A web-based attendance system using real-time face recognition. Built with Python, Flask, Dlib (via `face_recognition`), and a custom HTML/JavaScript frontend.

---

##🚀Tech Stack

- 🐍 Python 3.10  
- 🔥 Flask (backend API)  
- 🧠 Dlib + `face_recognition` (face encoding and recognition)  
- 📊 Pandas + OpenPyXL (for Excel attendance logging)  
- 🎨 HTML + CSS + JavaScript (frontend UI)

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo

2. Install Python 3.10
Python version 3.10.0
Installation Link: https://www.python.org/downloads/release/python-3100/

3. Install Cmake
cmake version 4.0.3
Installation Link: https://cmake.org/download/

4. Create Virtual Environment & Activate
py -3.10 -m venv faceenv
.\faceenv\Scripts\activate         # Windows
# source faceenv/bin/activate     # macOS/Linux

5. Install Dependencies
pip install -r requirements.txt

6. Run the App
python app.py
Open your browser and go to http://127.0.0.1:5000

📁 Project Structure
📦 your-repo/
├── app.py
├── requirements.txt
├── templates/
│   └── index.html
├── known_faces/
│   └── [username]/
│       └── 0.jpg, 1.jpg, ...
├── attendance.xlsx


🧑‍💻 Developed By
Hriday Das
🎓 B.Tech CSE | Full-Stack Web Developer/ Python & ML
🔗 LinkedIn: https://www.linkedin.com/in/hriday-das-390a61286/
