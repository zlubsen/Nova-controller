import cv2
import serial
import sys

coordinate_correction_x = 100/355
coordinate_correction_y = 100/266

def setupSerial():
    ser = serial.Serial()
    ser.port = 'COM4'
    ser.baudrate = 9600
    ser.open()
    return ser

def setupFaceRecognition():
    return cv2.CascadeClassifier("../data/haarcascades/haarcascade_frontalface_default.xml")

def setupVideoOutput():
    return cv2.VideoCapture(0)

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
    ser.write(center_x * coordinate_correction_x)
    ser.write(center_y * coordinate_correction_y)

def drawDetectedFaceHighlight(frame, face):
    x, y, w, h = face
    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

def loop(ser, video_capture, face_cascade):
    while True:
        frame = captureFrame(video_capture)
        faces = detectFaces(frame, face_cascade)

        for x,y,w,h in faces:
            centerX = x + w/2;
            centerY = y + h/2;

            drawDetectedFaceHighlight(frame, (x,y,w,h))

            writeToNova(ser, centerX, centerY)

        cv2.imshow('NovaVision', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if ser.in_waiting > 0:
            print(ser.readline().decode("utf-8"))

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
