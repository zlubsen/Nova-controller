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
        self.no_video_available_image = self.__initNotAvailableImage()

    def __createWindow(self):
        cv.namedWindow(NovaConfig.NOVA_WINDOW_NAME, cv.WINDOW_NORMAL)

    def __createVideoCapture(self):
        cap = cv.VideoCapture(0) # capture from default camera
        cap.set(cv.CAP_PROP_FRAME_WIDTH,NovaConfig.NOVA_CAMERA_CAPTURE_SIZE_X)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT,NovaConfig.NOVA_CAMERA_CAPTURE_SIZE_Y)
        return cap

    def captureFrame(self):
        ret, frame = self.video_capture.read()
        if ret:
            return frame
        else:
            return self.no_video_available_image

    def finaliseFrame(self, frame):
        cv.imshow(NovaConfig.NOVA_WINDOW_NAME, frame)

    def cleanup(self):
        self.video_capture.release()
        cv.destroyAllWindows()

    def __initNotAvailableImage(self):
        image = cv.imread(NovaConfig.NOVA_WINDOW_NOIMAGE_PATH)
        return cv.resize(image, (NovaConfig.NOVA_CAMERA_CAPTURE_SIZE_X, NovaConfig.NOVA_CAMERA_CAPTURE_SIZE_Y),interpolation = cv.INTER_AREA)
