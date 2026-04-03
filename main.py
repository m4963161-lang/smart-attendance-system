import cv2
import face_recognition
import os
import numpy as np
import requests

# 🌐 Your LIVE API
API_URL = "https://smart-attendance-system-gsut.onrender.com/attendance"

# 📂 Load images
path = 'images'
images = []
classNames = []

for cl in os.listdir(path):
    img = cv2.imread(f'{path}/{cl}')
    if img is None:
        continue
    images.append(img)
    classNames.append(os.path.splitext(cl)[0])

print("Loaded Students:", classNames)

# 🔍 Encode faces
def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        enc = face_recognition.face_encodings(img)
        if enc:
            encodeList.append(enc[0])
    return encodeList

encodeListKnown = findEncodings(images)
print("✅ Encoding Complete")

# 📡 Send attendance to API
def send_to_api(name):
    try:
        res = requests.get(API_URL, params={"name": name})
        print("📡 Sent:", res.json())
    except:
        print("❌ API Error")

# 🎥 Start camera
cap = cv2.VideoCapture(0)

markedNames = set()  # prevent duplicates

while True:
    success, img = cap.read()
    if not success:
        break

    imgS = cv2.resize(img, (0,0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()

            # Send only once
            if name not in markedNames:
                send_to_api(name)
                markedNames.add(name)

            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4

            cv2.rectangle(img, (x1,y1), (x2,y2), (0,255,0), 2)
            cv2.putText(img, name, (x1,y2+25),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

    cv2.imshow('Smart Attendance System', img)

    if cv2.waitKey(1) == 13:
        break

cap.release()
cv2.destroyAllWindows()