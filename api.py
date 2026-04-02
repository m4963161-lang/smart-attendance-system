import streamlit as st
import cv2
import face_recognition
import os
import numpy as np
import pandas as pd
from db import save_attendance
from db import save_login
from pymongo import MongoClient
from fastapi import FastAPI
from pymongo import MongoClient
from datetime import datetime

app = FastAPI()

client = MongoClient("YOUR_MONGO_ATLAS_URL")
db = client["attendence_db"]

@app.get("/")
def home():
    return {"message": "API Running"}

@app.post("/login")
def login(username: str):
     db["users"].insert_one({
        "username": username,
        "time": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    })
     return {"status": "saved"}

client = MongoClient("mongodb://localhost:27017/")
db = client["attendence_db"]
collection = db["records"]

# Session state for login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


if st.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.rerun()

st.title("🎓 Smart Attendance System")

# Load images
path = 'images'
images = []
classNames = []

for cl in os.listdir(path):
    img = cv2.imread(f'{path}/{cl}')
    if img is None:
        continue
    images.append(img)
    classNames.append(os.path.splitext(cl)[0])

st.write("Loaded Students:", classNames)

# Encode faces
def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img)
        if len(encodings) > 0:
            encodeList.append(encodings[0])
    return encodeList

encodeListKnown = findEncodings(images)
st.success("✅ Encoding Complete")

# Session state


# Login function
def login():
    st.title("🔐 Admin Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username != "" and password != "":
            st.session_state.logged_in = True
            st.session_state.user = username

            from db import save_login
            save_login(username)   # 🔥 SAVE LOGIN

            st.success(f"Welcome {username}")
            st.rerun()
        else:
            st.error("Enter credentials")

# 🔥 THIS LINE MUST BE HERE
if not st.session_state.logged_in:
    login()
    st.stop()
    
# Attendance function
def markAttendance(name):
    if name != "UNKNOWN":
        save_attendance(name)

# Start camera
run = st.button("▶ Start Camera")

FRAME_WINDOW = st.image([])

if run:
    cap = cv2.VideoCapture(0)

    while True:
        success, img = cap.read()
        if not success:
            st.error("Camera error")
            break

        imgS = cv2.resize(img, (0,0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):

            if len(encodeListKnown) == 0:
                continue

            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDis)

            name = "UNKNOWN"

            # 🔥 Improved matching
            if faceDis[matchIndex] < 0.6:
                name = classNames[matchIndex].upper()
                markAttendance(name)

            y1,x2,y2,x1 = faceLoc
            y1,x2,y2,x1 = y1*4,x2*4,y2*4,x1*4

            cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
            cv2.putText(img,name,(x1,y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2)

        FRAME_WINDOW.image(img, channels="BGR")

# =========================
# DATABASE VIEW
# =========================

st.divider()



data = list(collection.find({}, {"_id": 0}))
df = pd.DataFrame(data)
if not df.empty:
    df = df.reindex(columns=["name", "date", "time"], fill_value="")

st.subheader("📊 Attendance Records")

if not df.empty:

    select_all = st.checkbox("✅ Select All")
    df["Select"] = select_all

    edited_df = st.data_editor(df, use_container_width=True)

    # Delete selected
    if st.button("🗑 Delete Selected"):
     for _, row in edited_df.iterrows():
        if row["Select"]:
            collection.delete_one({
                "name": row["name"],
                "date": row["date"],   # ✅ ADD THIS
                "time": row["time"]
            })
    st.success("Deleted selected rows")

    # Download
    st.download_button("⬇ Download", df.to_csv(index=False), "attendance.csv")

    # Clear all
    if st.button("❌ Clear All Data"):
        collection.delete_many({})
        st.success("All data cleared")

else:
    st.info("No data found")
    
