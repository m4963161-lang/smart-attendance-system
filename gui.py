import cv2
import face_recognition
import os
import numpy as np
from datetime import datetime
import tkinter as tk

# Global control variable
running = False

# Load images
path = 'images'
images = []
classNames = []

for cl in os.listdir(path):
    curImg = cv2.imread(f'{path}/{cl}')
    if curImg is None:
        continue
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img)
        if len(encodings) > 0:
            encodeList.append(encodings[0])
    return encodeList

encodeListKnown = findEncodings(images)

def markAttendance(name):
    with open('attendance.csv', 'a+') as f:
        f.seek(0)
        data = f.readlines()
        nameList = [line.split(',')[0] for line in data]

        if name not in nameList:
            now = datetime.now()
            dtString = now.strftime('%H:%M:%S')
            f.writelines(f'\n{name},{dtString}')

# Start camera
def start_camera():
    global running
    running = True

    cap = cv2.VideoCapture(0)

    while running:
        success, img = cap.read()
        if not success:
            break

        imgS = cv2.resize(img, (0,0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):

            matches = face_recognition.compare_faces(encodeListKnown, encodeFace, tolerance=0.5)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

            matchIndex = np.argmin(faceDis)

            name = "UNKNOWN"

            if matches[matchIndex] and faceDis[matchIndex] < 0.5:
                name = classNames[matchIndex].upper()
                markAttendance(name)

            y1,x2,y2,x1 = faceLoc
            y1,x2,y2,x1 = y1*4,x2*4,y2*4,x1*4

            cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
            cv2.putText(img,name,(x1,y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2)

        cv2.imshow('Attendance Camera', img)

        if cv2.waitKey(1) == 13:
            break

    cap.release()
    cv2.destroyAllWindows()

# Stop camera
def stop_camera():
    global running
    running = False

# GUI
root = tk.Tk()
root.title("Smart Attendance System")
root.geometry("400x300")

label = tk.Label(root, text="Smart Attendance System", font=("Arial", 16))
label.pack(pady=20)

start_btn = tk.Button(root, text="Start Camera", command=start_camera,
                      width=20, bg="green", fg="white")
start_btn.pack(pady=10)

stop_btn = tk.Button(root, text="Stop Camera", command=stop_camera,
                     width=20, bg="orange", fg="white")
stop_btn.pack(pady=10)

exit_btn = tk.Button(root, text="Exit", command=root.destroy,
                     width=20, bg="red", fg="white")
exit_btn.pack(pady=10)

root.mainloop()