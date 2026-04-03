import cv2
import face_recognition
import os
import numpy as np
import requests
import time

# 🔗 FULL Render API URL (IMPORTANT)
API_URL = "https://smart-attendance-system-gsut.onrender.com/login"

# 📁 Load images
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
        encodes = face_recognition.face_encodings(img)
        if encodes:
            encodeList.append(encodes[0])
    return encodeList

encodeListKnown = findEncodings(images)
print("✅ Encoding Complete")

# 🎥 Start camera
cap = cv2.VideoCapture(0)

marked = set()  # prevent duplicate API calls

while True:
    success, img = cap.read()
    if not success:
        break

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faces = face_recognition.face_locations(imgS)
    encodes = face_recognition.face_encodings(imgS, faces)

    for encodeFace, faceLoc in zip(encodes, faces):

        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        matchIndex = np.argmin(faceDis)

        name = "UNKNOWN"

        if faceDis[matchIndex] < 0.5:
            name = classNames[matchIndex].upper()

            # 🔥 Send to API (only once per person)
            if name not in marked:
                try:
                    print(f"📡 Sending {name} to API...")

                    response = requests.post(
                        API_URL,
                        params={"username": name},
                        timeout=10
                    )

                    print("📡 Status:", response.status_code)
                    print("📡 Response:", response.text)

                    if response.status_code == 200:
                        print("✅ Attendance Marked:", name)
                        marked.add(name)
                    else:
                        print("❌ API Error:", response.status_code)

                except Exception as e:
                    print("❌ Connection Error:", e)
                    print("⏳ Retrying in 5 seconds...")
                    time.sleep(5)

        # 🎯 Draw rectangle
        y1, x2, y2, x1 = faceLoc
        y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4

        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(img, name, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("Smart Attendance System", img)

    # ❌ Press Q to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()