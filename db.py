from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client["attendence_db"]

# ✅ Attendance function
def save_attendance(name):
    now = datetime.now()
    data = {
        "name": name,
        "date": now.strftime("%d-%m-%Y"),
        "time": now.strftime("%H:%M:%S")
    }
    db["records"].insert_one(data)
    print("Saved attendance:", name)

# ✅ Login function
def save_login(username):
    data = {
        "username": username,
        "login_time": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    }
    db["users"].insert_one(data)
    print("Login saved:", username)