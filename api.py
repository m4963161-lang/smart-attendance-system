from fastapi import FastAPI
from datetime import datetime
from pymongo import MongoClient

app = FastAPI()

# 🔗 MongoDB Atlas Connection (REPLACE PASSWORD)
MONGO_URL = "mongodb+srv://admin:1234@cluster0.nmyolcj.mongodb.net/attendance_db?retryWrites=true&w=majority"

client = MongoClient(MONGO_URL)
db = client["attendance_db"]
collection = db["records"]

# ✅ Home
@app.get("/")
def home():
    return {"message": "API Running"}

# ✅ Save Attendance (browser + camera both work)
@app.get("/attendance")
def mark_attendance(name: str):
    record = {
        "name": name,
        "time": datetime.now().strftime("%H:%M:%S"),
        "date": datetime.now().strftime("%d-%m-%Y")
    }

    collection.insert_one(record)

    return {
        "status": "saved",
        "data": record
    }

# ✅ Get All Records
@app.get("/records")
def get_records():
    data = list(collection.find({}, {"_id": 0}))
    return {"data": data}