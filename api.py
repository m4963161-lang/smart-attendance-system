from fastapi import FastAPI
from datetime import datetime
from pymongo import MongoClient
import certifi

app = FastAPI()

# ✅ MongoDB Atlas URL (PUT YOUR REAL PASSWORD)
MONGO_URL = "mongodb+srv://admin:1234@cluster0.nmyolcj.mongodb.net/attendance_db?retryWrites=true&w=majority"

# ✅ FIX: SSL CERTIFICATE
client = MongoClient(MONGO_URL, tlsCAFile=certifi.where())

db = client["attendance_db"]
collection = db["records"]

@app.get("/")
def home():
    return {"message": "API Running"}

@app.get("/attendance")
def mark_attendance(name: str):
    record = {
        "name": name,
        "time": datetime.now().strftime("%H:%M:%S"),
        "date": datetime.now().strftime("%d-%m-%Y")
    }

    try:
        collection.insert_one(record)
        return {"status": "saved"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/records")
def get_records():
    try:
        data = list(collection.find({}, {"_id": 0}))
        return {"data": data}
    except Exception as e:
        return {"error": str(e)}