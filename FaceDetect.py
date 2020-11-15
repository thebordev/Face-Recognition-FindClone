import numpy as np
import face_recognition
import cv2
from PIL import ImageFont, ImageDraw, Image
import os
from datetime import datetime
import FindCloneAPI

path = 'KnownFaces'
images = []
classNames = []

cap = cv2.VideoCapture(0)

def face_detect():
    myList = os.listdir(path)
    print(myList)

    for cls in myList:
        curImg = cv2.imread(f'{path}/{cls}')
        images.append(curImg)
        classNames.append(os.path.splitext(cls)[0])

    print(classNames)

    def findEncodings(images):
        encodeList = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        return encodeList

    def markAttendance(name):
        with open("Attendance.csv", "r+") as f:
            myDataList = f.readlines()
            nameList = []
            for line in myDataList:
                entry = line.split(',')
                nameList.append(entry[0])
            if name not in nameList:
                now = datetime.now()
                dtString = now.strftime("%H:%M:%S")
                f.writelines(f'\n{name}, {dtString}')

    encodeListKnown = findEncodings(images)
    print("Декодирование закончено")

    while True:
        success, img = cap.read()
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurFrame = face_recognition.face_locations(imgS)
        encodeCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        for encodeFace, faceLoc in zip(encodeCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            #print(faceDis)
            matchIndex = np.argmin(faceDis)

            name = 'Unknown'

            if matches[matchIndex]:
                name = classNames[matchIndex]
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4

                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 0), 3)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 0, 0), cv2.FILLED)

                font_path = 'Fonts/Roboto-Regular.ttf'
                font = ImageFont.truetype(font_path, 32)
                img_pil = Image.fromarray(img)
                b, g, r, a = 255, 255, 255, 0
                draw = ImageDraw.Draw(img_pil)
                draw.text((x1 + 6, y2 - 35), str(name), font=font, fill=(b, g, r, a))
                frame = np.array(img_pil)
                markAttendance(name)

            else:
                filename = 'KnownFaces/face.jpg'
                cv2.imwrite(filename, img)
                print("Лицо сохранено")
                find_clone(filename)

        cv2.imshow("WebCam", frame)
        cv2.waitKey(1)

def find_clone(img):
    find = FindCloneAPI.FindCloneAPI()
    find.login()
    find.upload(img)
    name = 'KnownFaces/' + str(find.out()) + '.jpg'
    os.rename(img, name)
    face_detect()

face_detect()
