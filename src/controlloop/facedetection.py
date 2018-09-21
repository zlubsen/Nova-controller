import cv2 as cv
from config.constants import NovaConstants
from config.config import NovaConfig
from utils.commandtype_enum import CommandType

class FaceDetectionControlLoop:
    def __init__(self, serial_communication):
        self.commands_send = 0
        self.commands_acked = 0
        self.serial_comm = serial_communication
        self.face_cascade = self.__setupFaceRecognition()

    def __setupFaceRecognition(self):
        return cv.CascadeClassifier(NovaConfig.FACE_DETECTION_FACE_CASCADE_PATH)

    def __detectFaces(self, frame, faceCascade):
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv.CASCADE_SCALE_IMAGE
        )
        return faces

    def __drawDetectedFaceHighlight(self, frame, face):
        x, y, w, h = face
        cv.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    def __detectAndProcessFaces(self, frame):
        faces = self.__detectFaces(frame, self.face_cascade)

        retX = -1
        retY = -1
        found = False

        for (x,y,w,h) in faces:
            centerX = x + w/2;
            centerY = y + h/2;

            self.__drawDetectedFaceHighlight(frame, (x,y,w,h))

            # TODO what to do when multiple faces are detected; now only the last one is transmitted
            found = True
            retX = centerX
            retY = centerY

        return (found, retX, retY)

    def __allCommandsAcknowledged(self):
        return self.commands_send is self.commands_acked

    def __writeCoordinates(self, center_x, center_y):
        x = int(center_x * NovaConfig.FACE_DETECTION_COORDINATE_CORRECTION_X)
        y = int(center_y * NovaConfig.FACE_DETECTION_COORDINATE_CORRECTION_Y)

        modcode = NovaConstants.MOD_FACE_DETECTION
        opcode = NovaConstants.OP_FACE_DETECTION_SET_COORDINATES
        args = [x, y, 0]

        self.serial_comm.writeCommand(modcode, opcode, args)
        self.commands_send += 1

    def __processResponses(self, cmds):
        for cmd in cmds:
            if cmd[0] == CommandType.NOVA:
                (type, modcode, opcode, arg1, arg2, arg3) = cmd
                if modcode is NovaConstants.MOD_FACE_DETECTION and opcode is NovaConstants.OP_FACE_DETECTION_ACK_COORDINATES:
                    self.commands_acked += 1
                    cmds.remove(cmd)

    def run(self, cmds, frame):
        self.__processResponses(cmds)

        (found, x,y) = self.__detectAndProcessFaces(frame)
        if self.__allCommandsAcknowledged() and found:
            self.__writeCoordinates(x, y)

    def cleanup(self):
        pass
