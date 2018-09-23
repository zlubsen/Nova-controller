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

    # module codes
    MOD_STATUS_NOVA = '0'
    MOD_JOYSTICK_CONTROL_ABOLUTE = '1'
    MOD_JOYSTICK_CONTROL_RELATIVE = '2'
    MOD_EXTERNAL_INPUT_CONTROL = '3'
    MOD_DISTANCE_AVOIDANCE = '4'
    MOD_FACE_DETECTION = '5'

    # operation codes
    OP_STATUS_RECEIVE_SERVO_1 = '1'             # (degree in arg1)
    OP_STATUS_RECEIVE_SERVO_2 = '2'             # (degree in arg1)
    OP_STATUS_RECEIVE_SERVO_3 = '3'             # (degree in arg1)
    OP_STATUS_RECEIVE_SERVO_4 = '4'             # (degree in arg1)
    OP_STATUS_RECEIVE_SERVO_5 = '5'             # (degree in arg1)
    OP_STATUS_RECEIVE_USS = '6'                 # (distance in arg1)
    OP_STATUS_RECEIVE_JOY_LEFT = '7'            # (x, y, pushed in arg1, arg2, arg3)
    OP_STATUS_RECEIVE_JOY_RIGHT = '8'           # (x, y, pushed in arg1, arg2, arg3)
    OP_STATUS_SEND_SET_MODE = '9'               # (set new modulecode as arg1)
    OP_STATUS_RECEIVE_DISTANCE_PID = '10'       # (Kp, Ki, Kd values in arg1, arg2, arg3)
    OP_STATUS_RECEIVE_FACEDETECT_PID_X = '11'   # (Kp, Ki, Kd values in arg1, arg2, arg3)
    OP_STATUS_RECEIVE_FACEDETECT_PID_Y = '12'   # (Kp, Ki, Kd values in arg1, arg2, arg3)

    OP_DISTANCE_SET_MIN_DIST = '1'              # (new minimum distance in arg1)
    OP_DISTANCE_SET_MAX_DIST = '2'              # (new maximum distance in arg1)
    OP_DISTANCE_SET_SETPOINT = '3'              # (new setpoint in arg1)
    OP_DISTANCE_SET_PID_TUNING = '4'            # (p, i, d in arg1, arg2, arg3)

    OP_FACE_DETECTION_SET_COORDINATES = '1'     # (x, y) in arg1, arg2)
    OP_FACE_DETECTION_ACK_COORDINATES = '2'     # ack for received coordinates
    OP_FACE_DETECTION_SET_X_SETPOINT = '3'      # (new setpoint in arg1)
    OP_FACE_DETECTION_SET_Y_SETPOINT = '4'      # (new setpoint in arg1)
    OP_FACE_DETECTION_SET_X_PID_TUNING = '5'    # (p, i, d in arg1, arg2, arg3)
    OP_FACE_DETECTION_SET_Y_PID_TUNING = '6'    # (p, i, d in arg1, arg2, arg3)

    OP_EXTERNAL_INPUT_HEAD_MOVE_FRONTBACK = '1'     # (# steps in arg1)
    OP_EXTERNAL_INPUT_HEAD_ROTATE_LEFTRIGHT = '2'   # etc
    OP_EXTERNAL_INPUT_HEAD_ROTATE_UPDOWN = '3'
    OP_EXTERNAL_INPUT_BODY_MOVE_RIGHTLEFT = '4'
    OP_EXTERNAL_INPUT_HEAD_MOVE_UPDOWN = '5'

    #OP_EXTERNAL_INPUT_HEAD_MOVE_FRONT = '1'        # (# steps/degrees in arg1)
    #OP_EXTERNAL_INPUT_HEAD_MOVE_BACK = '2'         # etc
    #OP_EXTERNAL_INPUT_HEAD_MOVE_UP = '3'
    #OP_EXTERNAL_INPUT_HEAD_MOVE_DOWN = '4'
    #OP_EXTERNAL_INPUT_BODY_MOVE_RIGHT = '5'
    #OP_EXTERNAL_INPUT_BODY_MOVE_LEFT = '6'
    #OP_EXTERNAL_INPUT_HEAD_ROTATE_UP = '7'
    #OP_EXTERNAL_INPUT_HEAD_ROTATE_DOWN = '8'
    #OP_EXTERNAL_INPUT_HEAD_ROTATE_LEFT = '9'
    #OP_EXTERNAL_INPUT_HEAD_ROTATE_RIGHT = '10'

    #OP_EXTERNAL_INPUT_HEAD_MOVE_FB_ABS = '0'       # (# signed degrees in arg1)
    #OP_EXTERNAL_INPUT_HEAD_MOVE_FB_REL = '1'       # (# signed steps in arg1)
    #OP_EXTERNAL_INPUT_HEAD_MOVE_UD_ABS = '2'       # etc
    #OP_EXTERNAL_INPUT_HEAD_MOVE_UD_REL = '3'
    #OP_EXTERNAL_INPUT_BODY_MOVE_LR_ABS = '4'
    #OP_EXTERNAL_INPUT_BODY_MOVE_LR_REL = '5'
    #OP_EXTERNAL_INPUT_HEAD_ROTATE_UD_ABS = '6'
    #OP_EXTERNAL_INPUT_HEAD_ROTATE_UD_REL = '7'
    #OP_EXTERNAL_INPUT_HEAD_ROTATE_LR_ABS = '8'
    #OP_EXTERNAL_INPUT_HEAD_ROTATE_LR_REL = '9'
