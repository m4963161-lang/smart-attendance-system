from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

# Temporary storage (works online)
attendance_data = []

# Home route
@app.get("/")
def home():
    return {"message": "API Running"}

# ✅ Attendance (GET → works in browser)
@app.get("/attendance")
def mark_attendance(name: str):
    record = {
        "name": name,
        "time": datetime.now().strftime("%H:%M:%S"),
        "date": datetime.now().strftime("%d-%m-%Y")
    }
    attendance_data.append(record)
    return {
        "status": "saved",
        "data": record
    }

# Get all records
@app.get("/records")
def get_records():
    return {"data": attendance_data}