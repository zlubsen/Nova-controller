class MetaConst(type):
    def __getattr__(cls, key):
        return cls[key]

    def __setattr__(cls, key, value):
        raise TypeError

class Const(object, metaclass=MetaConst):
    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        raise TypeError

class NovaConfig(Const):
    SERIAL_BAUDRATE = 28800
    SERIAL_PORT_WINDOWS = 'COM4'
    SERIAL_PORT_MACOS = '' # TODO set correct port for macos
    SERIAL_PORT_LINUX = '' # TODO set correct port for Linux
    SERIAL_RECONNECT_MS = 1000

    COMPCOMM_STATUS_PUBSUB_SOCKET = 8888
    COMPCOMM_STATUS_PUB_URI = f"tcp://*:{COMPCOMM_STATUS_PUBSUB_SOCKET}"
    COMPCOMM_STATUS_SUB_URI = f"tcp://localhost:{COMPCOMM_STATUS_PUBSUB_SOCKET}"
    COMPCOMM_COMMAND_SOCKET = 8889
    COMPCOMM_COMMAND_URI = f"tcp://*:{COMPCOMM_COMMAND_SOCKET}"

    NOVA_WINDOW_NAME = 'Nova'
    NOVA_WINDOW_NOIMAGE_PATH = "images/no_image_available.png"

    #NOVA_CAMERA_CAPTURE_SIZE_X = 320
    #NOVA_CAMERA_CAPTURE_SIZE_Y = 240
    NOVA_CAMERA_CAPTURE_SIZE_X = 640
    NOVA_CAMERA_CAPTURE_SIZE_Y = 480

    STARTUP_MODE = "joystick_absolute"

    TUNE_PID_STEPSIZE = 0.005

    # module specific constants
    STATUS_PUBLISH_FREQUENCY_MS = 2000

    EXTERNAL_INPUT_STEPSIZE_DEGREES = 3
    EXTERNAL_INPUT_MOUSE_FREQUENCY_MS = 15

    FACE_DETECTION_FACE_CASCADE_PATH = "data/haarcascades/haarcascade_frontalface_default.xml"
    #FACE_DETECTION_COORDINATE_CORRECTION_X = 100 / 177 # 320x240 to 180x180
    #FACE_DETECTION_COORDINATE_CORRECTION_Y = 100 / 133 # 320x240 to 180x180
    FACE_DETECTION_COORDINATE_CORRECTION_X = 100 / 355 # 640x480 to 180x180
    FACE_DETECTION_COORDINATE_CORRECTION_Y = 100 / 266 # 640x480 to 180x180
