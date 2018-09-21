# class that maintains the window and processed frames
# 1. capture a frame
# 2. let controlloops apply appropriate processing (e.g., face detection)
# 3. decorate frame with additional operations (e.g., display help text)

import cv2 as cv
from config.config import NovaConfig
from utils.commandtype_enum import CommandType

class WindowBaseLoop:
    def __init__(self):
        self.__createWindow()
        self.video_capture = self.__createVideoCapture()
        self.frame = None

    def __createWindow(self):
        cv.namedWindow(NovaConfig.NOVA_WINDOW_NAME, cv.WINDOW_AUTOSIZE)

    def __createVideoCapture(self):
        cap = cv.VideoCapture(0) # capture from default camera
        cap.set(cv.CAP_PROP_FRAME_WIDTH,NovaConfig.FACE_DETECTION_CAPTURE_SIZE_X)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT,NovaConfig.FACE_DETECTION_CAPTURE_SIZE_Y)
        return cap

    def captureFrame(self):
        ret, frame = self.video_capture.read()
        return frame

    def finaliseFrame(self, frame):
        cv.imshow(NovaConfig.NOVA_WINDOW_NAME, frame)

    def cleanup(self):
        self.video_capture.release()
        cv.destroyAllWindows()
