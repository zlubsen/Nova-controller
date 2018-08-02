import cv2
import serial
import sys
import time

coordinate_correction_x = 100 / 177 #100/355
coordinate_correction_y = 100 / 133 #100/266

def setupSerial():
    ser = serial.Serial()
    ser.port = 'COM4'
    ser.baudrate = 9600
    ser.open()
    return ser

def setupFaceRecognition():
    return cv2.CascadeClassifier("../data/haarcascades/haarcascade_frontalface_default.xml")

def setupVideoOutput():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,240)
    return cap

def captureFrame(video):
    ret, frame = video.read()
    return frame

def detectFaces(frame, faceCascade):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    return faces

def writeToNova(ser, center_x, center_y):
    x = int(center_x * coordinate_correction_x)
    y = int(center_y * coordinate_correction_y)
    #print("send: {0}, {1}".format(x,y))
    ser.write(x.to_bytes(1,'big'))
    ser.write(y.to_bytes(1,'big'))

def drawDetectedFaceHighlight(frame, face):
    x, y, w, h = face
    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

def loop(ser, video_capture, face_cascade):
    lastTime = int(round(time.time() * 1000))
    while True:
        frame = captureFrame(video_capture)
        faces = detectFaces(frame, face_cascade)

        for (x,y,w,h) in faces:
            centerX = x + w/2;
            centerY = y + h/2;

            drawDetectedFaceHighlight(frame, (x,y,w,h))

            writeToNova(ser, centerX, centerY)

        cv2.imshow('NovaVision', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if ser.in_waiting > 0:
            print(ser.readline().decode("utf-8"))

        currentTime = int(round(time.time() * 1000))
        duration = currentTime - lastTime
        lastTime = currentTime
        print("loop took: {}".format(duration))
#        time.sleep(1)

def main():
    ser = setupSerial()
    face_cascade = setupFaceRecognition()
    video_capture = setupVideoOutput()

    loop(ser, video_capture, face_cascade)

    return (ser, video_capture)

def cleanup(ser, video_capture):
    video_capture.release()
    cv2.destroyAllWindows()
    ser.close()

if __name__ == '__main__':
    (ser, cap) = main()
    cleanup(ser, cap)
