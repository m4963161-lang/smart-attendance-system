from fastapi import FastAPI
from datetime import datetime
from pymongo import MongoClient
import certifi
import os
from fastapi import Query

app = FastAPI()

# ✅ USE ENV VARIABLE (IMPORTANT FOR RENDER)
MONGO_URL = os.getenv("mongodb+srv://admin:1234@cluster0.nmyolcj.mongodb.net/attendance_db?retryWrites=true&w=majority")

# ✅ CONNECT (FIXED)
client = MongoClient(MONGO_URL, tlsCAFile=certifi.where())

db = client["attendance_db"]
collection = db["records"]

@app.get("/")
def home():
    return {"message": "API Running"}



@app.get("/attendance")
def mark_attendance(name: str):
    try:
        today = datetime.now().strftime("%d-%m-%Y")

        # ✅ CHECK IF ALREADY MARKED
        existing = collection.find_one({"name": name, "date": today})

        if existing:
            return {"status": "already marked"}

        record = {
            "name": name,
            "time": datetime.now().strftime("%H:%M:%S"),
            "date": today
        }

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
    
    
@app.delete("/delete")
def delete_record(name: str = Query(...), date: str = Query(...)):
    try:
        result = collection.delete_many({"name": name, "date": date})
        return {"deleted_count": result.deleted_count}
    except Exception as e:
        return {"error": str(e)}