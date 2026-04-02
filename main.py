import cv2
import face_recognition
import os
import numpy as np
from datetime import datetime

# Path to images
path = 'images'

# Auto-create folder if not exists
if not os.path.exists(path):
    os.makedirs(path)
    print("📁 'images' folder created. Add student images and run again.")
    exit()

images = []
classNames = []

# Load images
for cl in os.listdir(path):
    curImg = cv2.imread(f'{path}/{cl}')
    if curImg is None:
        continue
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])

print("Loaded Students:", classNames)

# Encode faces
def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img)

        if len(encodings) > 0:
            encodeList.append(encodings[0])
        else:
            print("⚠️ No face found in one image, skipping...")

    return encodeList

# Mark attendance
def markAttendance(name):
    with open('attendance.csv', 'a+') as f:
        f.seek(0)
        data = f.readlines()
        nameList = [line.split(',')[0] for line in data]

        if name not in nameList:
            now = datetime.now()
            dtString = now.strftime('%H:%M:%S')
            f.writelines(f'\n{name},{dtString}')
            print(f"✅ Attendance Marked: {name}")

# Encode known faces
encodeListKnown = findEncodings(images)
print("✅ Encoding Complete")

# Start webcam
cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    if not success:
        print("❌ Camera not working")
        break

    # Resize for faster processing
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    # Detect faces
    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):

        if len(encodeListKnown) == 0:
            continue

        matches = face_recognition.compare_faces(encodeListKnown, encodeFace, tolerance=0.5)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

        matchIndex = np.argmin(faceDis)

        # Default name
        name = "UNKNOWN"

        if matches[matchIndex] and faceDis[matchIndex] < 0.5:
            name = classNames[matchIndex].upper()

        # Scale back face location
        y1, x2, y2, x1 = faceLoc
        y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4

        # Draw rectangle
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.rectangle(img, (x1, y2-35), (x2, y2), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, name, (x1+6, y2-6),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

        # Mark attendance if recognized
        if name != "UNKNOWN":
            markAttendance(name)

    cv2.imshow('Smart Attendance System', img)

    # Press ENTER to exit
    if cv2.waitKey(1) == 13:
        break

cap.release()
cv2.destroyAllWindows()

