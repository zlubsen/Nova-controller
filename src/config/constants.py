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

class NovaConstants(Const):
    # command template
    CMD_START_MARKER = '>'
    CMD_END_MARKER = '<'
    CMD_SEPARATOR = ':'
    CMD_TEMPLATE = CMD_START_MARKER + "{}:{}:{}:{}:{}" + CMD_END_MARKER

    SERIAL_BAUDRATE = 28800
    SERIAL_PORT_WINDOWS = 'COM4'
    SERIAL_PORT_MACOS = '' # TODO set correct port for macos
    SERIAL_PORT_LINUX = '' # TODO set correct port for Linux

    COMPCOMM_STATUS_SOCKET = 8888
    COMPCOMM_COMMAND_SOCKET = 8889

    # module codes
    MOD_STATUS_NOVA = '0'
    MOD_JOYSTICK_CONTROL_ABOLUTE = '1'
    MOD_JOYSTICK_CONTROL_RELATIVE = '2'
    MOD_KEYBOARD_MOUSE_CONTROL = '3'
    MOD_DISTANCE_AVOIDANCE = '4'
    MOD_FACE_DETECTION = '5'

    # operation codes
    OP_STATUS_RECEIVE_SERVO_1 = '1'         # (degree in arg1)
    OP_STATUS_RECEIVE_SERVO_2 = '2'         # (degree in arg1)
    OP_STATUS_RECEIVE_SERVO_3 = '3'         # (degree in arg1)
    OP_STATUS_RECEIVE_SERVO_4 = '4'         # (degree in arg1)
    OP_STATUS_RECEIVE_SERVO_5 = '5'         # (degree in arg1)
    OP_STATUS_RECEIVE_USS = '6'             # (distance in arg1)
    OP_STATUS_RECEIVE_JOY_LEFT = '7'        # (x, y, pushed in arg1, arg2, arg3)
    OP_STATUS_RECEIVE_JOY_RIGHT = '8'        # (x, y, pushed in arg1, arg2, arg3)
    OP_STATUS_SEND_SET_MODE = '9'           # (set new modulecode as arg1)

    OP_DISTANCE_SET_MIN_DIST = '1'          # (new minimum distance in arg1)
    OP_DISTANCE_SET_MAX_DIST = '2'          # (new maximum distance in arg1)
    OP_DISTANCE_SET_SETPOINT = '3'          # (new setpoint in arg1)
    OP_DISTANCE_SET_PID_TUNING = '4'        # (p, i, d in arg1, arg2, arg3)

    OP_FACE_DETECTION_X_SETPOINT = '1'      # (new setpoint in arg1)
    OP_FACE_DETECTION_Y_SETPOINT = '2'      # (new setpoint in arg1)
    OP_FACE_DETECTION_X_PID_TUNING = '3'    # (p, i, d in arg1, arg2, arg3)
    OP_FACE_DETECTION_Y_PID_TUNING = '4'    # (p, i, d in arg1, arg2, arg3)
    OP_FACE_DETECTION_SET_COORDINATES = '5' # (x, y) in arg1, arg2)
    OP_FACE_DETECTION_ACK_COORDINATES = '6' # ack for received coordinates

    # module specific constants
    FACE_DETECTION_WINDOW_NAME = 'NovaVision'
    FACE_DETECTION_FACE_CASCADE_PATH = "../data/haarcascades/haarcascade_frontalface_default.xml"
    FACE_DETECTION_CAPTURE_SIZE_X = 320
    FACE_DETECTION_CAPTURE_SIZE_Y = 240
    FACE_DETECTION_COORDINATE_CORRECTION_X = 100 / 177 # 320x240 to 180x180
    FACE_DETECTION_COORDINATE_CORRECTION_Y = 100 / 133 # 320x240 to 180x180
    #FACE_DETECTION_COORDINATE_CORRECTION_X = 100 / 355 # 640x480 to 180x180
    #FACE_DETECTION_COORDINATE_CORRECTION_Y = 100 / 266 # 640x480 to 180x180
