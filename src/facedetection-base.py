import cv2
import serial
import sys
import time

coordinate_correction_x = 100 / 177 #100/355
coordinate_correction_y = 100 / 133 #100/266

TO_NOVA_COMMAND_TEMPLATE = ">{}:{}:{}:{}:{}<"
FROM_NOVA_ACK_TEMPLATE = "&\r\n"

commands_send = 0
commands_acked = 0

def setupSerial():
    ser = serial.Serial()
    ser.port = 'COM4'
    ser.baudrate = 28800 #9600
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
    global commands_send
    x = int(center_x * coordinate_correction_x)
    y = int(center_y * coordinate_correction_y)

    cmd = TO_NOVA_COMMAND_TEMPLATE.format(0,0,x,y,0).encode()
    #print("[cntr] {}".format(cmd))
    ser.write(cmd)
    commands_send += 1

def drawDetectedFaceHighlight(frame, face):
    x, y, w, h = face
    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

def captureAndDetectFaces(ser, video_capture, face_cascade):
    frame = captureFrame(video_capture)
    faces = detectFaces(frame, face_cascade)

    retX = -1
    retY = -1
    found = False

    for (x,y,w,h) in faces:
        centerX = x + w/2;
        centerY = y + h/2;

        drawDetectedFaceHighlight(frame, (x,y,w,h))

        # TODO what to do when multiple faces are detected; now only the last one is transmitted
        found = True
        retX = centerX
        retY = centerY

    cv2.imshow('NovaVision', frame)
    return (found, retX, retY)

def loop(ser, video_capture, face_cascade):
    while True:
        (found, x,y) = captureAndDetectFaces(ser, video_capture, face_cascade)
        if allCommandsAcknowledged() and found:
            writeToNova(ser, x, y)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        checkResponses(ser)

def allCommandsAcknowledged():
    return commands_send == commands_acked

def checkResponses(ser):
    global commands_acked
    if ser.in_waiting > 0:
        line = ser.readline().decode("utf-8")
        print("[nova] {}".format(line))
        if line == FROM_NOVA_ACK_TEMPLATE:
            commands_acked += 1

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
