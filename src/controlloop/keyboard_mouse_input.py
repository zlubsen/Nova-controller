import cv2 as cv
from collections import deque
from enum import Enum
from config.constants import NovaConstants
from config.config import NovaConfig
from utils.commandtype_enum import CommandType
from utils.frequencytimer import FrequencyTimer

class NovaMove(Enum):
    QUIT_CONTROLLER = 1
    HEAD_MOVE_FRONT = 2
    HEAD_MOVE_BACK = 3
    HEAD_MOVE_UP = 4
    HEAD_MOVE_DOWN = 5
    BODY_MOVE_RIGHT = 6
    BODY_MOVE_LEFT = 7
    HEAD_ROTATE_UP = 8
    HEAD_ROTATE_DOWN = 9
    HEAD_ROTATE_LEFT = 10
    HEAD_ROTATE_RIGHT = 11
    SET_MODE_JOYSTICK_ABSOLUTE = 12
    SET_MODE_JOYSTICK_RELATIVE = 13
    SET_MODE_EXTERNAL_INPUT = 14
    SET_MODE_DISTANCE_AVOIDANCE = 15
    SET_MODE_FACE_DETECTION = 16

class KeyboardMouseInputLoop:
    # dict that maps defined actions by id to (key_binding, mouse_binding, int_id, positive_direction, description, action) tuples
    actionDict = {
        NovaMove.QUIT_CONTROLLER : ('q', 'NONE', '', "Quit the controller", lambda self: self.__processControllerOperationCommand(NovaMove.QUIT_CONTROLLER)),

        NovaMove.SET_MODE_JOYSTICK_ABSOLUTE : ('1', 'NONE', NovaConstants.MOD_JOYSTICK_CONTROL_ABOLUTE, "Set mode to Joystick - absolute control", lambda self: self.__processModeSelectionCommand(NovaMove.SET_MODE_JOYSTICK_ABSOLUTE)),
        NovaMove.SET_MODE_JOYSTICK_RELATIVE : ('2', 'NONE', NovaConstants.MOD_JOYSTICK_CONTROL_RELATIVE, "Set mode to Joystick - relative control", lambda self: self.__processModeSelectionCommand(NovaMove.SET_MODE_JOYSTICK_RELATIVE)),
        NovaMove.SET_MODE_EXTERNAL_INPUT : ('3', 'NONE', NovaConstants.MOD_EXTERNAL_INPUT_CONTROL, "Set mode to External input (keyboard, mouse, API)", lambda self: self.__processModeSelectionCommand(NovaMove.SET_MODE_EXTERNAL_INPUT)),
        NovaMove.SET_MODE_DISTANCE_AVOIDANCE : ('4', 'NONE', NovaConstants.MOD_DISTANCE_AVOIDANCE, "Set mode to Distance Avoid", lambda self: self.__processModeSelectionCommand(NovaMove.SET_MODE_DISTANCE_AVOIDANCE)),
        NovaMove.SET_MODE_FACE_DETECTION : ('5', 'NONE', NovaConstants.MOD_FACE_DETECTION, "Set mode to Face Detection", lambda self: self.__processModeSelectionCommand(NovaMove.SET_MODE_FACE_DETECTION)),

        NovaMove.HEAD_MOVE_FRONT : ('e', 'MOUSE_SCROLL_PLUS', NovaConstants.OP_EXTERNAL_INPUT_HEAD_MOVE_FRONTBACK, "Head movement - forwards", lambda self: self.__processMoveCommand(NovaMove.HEAD_MOVE_FRONT, True)),
        NovaMove.HEAD_MOVE_BACK : ('d', 'MOUSE_SCROLL_MINUS', NovaConstants.OP_EXTERNAL_INPUT_HEAD_MOVE_FRONTBACK, "Head movement - backwards", lambda self: self.__processMoveCommand(NovaMove.HEAD_MOVE_BACK, False)),
        NovaMove.HEAD_MOVE_UP : ('g', 'MOUSE_LBUTTON_Y_PLUS', NovaConstants.OP_EXTERNAL_INPUT_HEAD_MOVE_UPDOWN, "Body movement - up", lambda self: self.__processMoveCommand(NovaMove.HEAD_MOVE_UP, True)),
        NovaMove.HEAD_MOVE_DOWN : ('h', 'MOUSE_LBUTTON_Y_MINUS', NovaConstants.OP_EXTERNAL_INPUT_HEAD_MOVE_UPDOWN, "Body movement - down", lambda self: self.__processMoveCommand(NovaMove.HEAD_MOVE_DOWN, False)),

        NovaMove.BODY_MOVE_RIGHT : ('f', 'MOUSE_LBUTTON_X_MINUS', NovaConstants.OP_EXTERNAL_INPUT_BODY_MOVE_RIGHTLEFT, "Body movement - right", lambda self: self.__processMoveCommand(NovaMove.BODY_MOVE_RIGHT, True)),
        NovaMove.BODY_MOVE_LEFT : ('s', 'MOUSE_LBUTTON_X_PLUS', NovaConstants.OP_EXTERNAL_INPUT_BODY_MOVE_RIGHTLEFT, "Body movement - left", lambda self: self.__processMoveCommand(NovaMove.BODY_MOVE_LEFT, False)),

        NovaMove.HEAD_ROTATE_UP : ('i', 'MOUSE_RBUTTON_Y_PLUS', NovaConstants.OP_EXTERNAL_INPUT_HEAD_ROTATE_UPDOWN, "Head rotation - up", lambda self: self.__processMoveCommand(NovaMove.HEAD_ROTATE_UP, True)),
        NovaMove.HEAD_ROTATE_DOWN : ('k', 'MOUSE_RBUTTON_Y_MINUS', NovaConstants.OP_EXTERNAL_INPUT_HEAD_ROTATE_UPDOWN, "Head rotation - down", lambda self: self.__processMoveCommand(NovaMove.HEAD_ROTATE_DOWN, False)),
        NovaMove.HEAD_ROTATE_LEFT : ('j', 'MOUSE_RBUTTON_X_PLUS', NovaConstants.OP_EXTERNAL_INPUT_HEAD_ROTATE_LEFTRIGHT, "Head rotation - left", lambda self: self.__processMoveCommand(NovaMove.HEAD_ROTATE_LEFT, True)),
        NovaMove.HEAD_ROTATE_RIGHT : ('l', 'MOUSE_RBUTTON_X_MINUS', NovaConstants.OP_EXTERNAL_INPUT_HEAD_ROTATE_LEFTRIGHT, "Head rotation - right", lambda self: self.__processMoveCommand(NovaMove.HEAD_ROTATE_RIGHT, False))
    }

    ACTION_KEY_INDEX = 0
    ACTION_MOUSE_INDEX = 1
    ACTION_OPERATION_ID_INDEX = 2
    ACTION_DESCRIPTION_INDEX = 3
    ACTION_LAMBDA_INDEX = 4

    def __init__(self, serial_communication):
        self.serial_comm = serial_communication
        key_index, mouse_index = self.__buildInputIndexes()
        self.key_index = key_index
        self.mouse_index = mouse_index

        self.running = True
        self.move_commands = deque()

        self.mouse_move_on = False
        cv.setMouseCallback(NovaConfig.NOVA_WINDOW_NAME, self.__onMouse)
        self.mouse_timer = FrequencyTimer(NovaConfig.EXTERNAL_INPUT_MOUSE_FREQUENCY_MS)

    # build and index of possible keys/mouse events, (dict key as ord('x')) so we can search based on the pressed key and mouse event
    def __buildInputIndexes(self):
        key_index = {}
        mouse_index = {}

        for id, tuple in self.actionDict.items():
            (key, mouse, op_id, desc, action) = tuple
            key_index[ord(key)] = id
            mouse_index[mouse] = id

        return key_index, mouse_index

    def __buildMouseIndex(self):
        mouse_index = {}

    def __readKeyInput(self):
        key_pressed = (cv.waitKey(1) & 0xFF)
        if key_pressed in self.key_index:
            operation = self.key_index[key_pressed]
            self.actionDict[operation][self.ACTION_LAMBDA_INDEX](self)

    def __processControllerOperationCommand(self, operation):
        if operation == NovaMove.QUIT_CONTROLLER:
            self.running = False
            print("[cntr] Closing Nova controller... Bye")

    def __processModeSelectionCommand(self, operation):
        new_mod_code = self.actionDict[operation][self.ACTION_OPERATION_ID_INDEX]
        args = [new_mod_code,0,0]
        cmd = (CommandType.INPUT, NovaConstants.MOD_STATUS_NOVA, NovaConstants.OP_STATUS_SEND_SET_MODE, args)
        self.move_commands.append(cmd)

    def __processMoveCommand(self, move, positive_direction):
        degrees = NovaConfig.EXTERNAL_INPUT_STEPSIZE_DEGREES if positive_direction else -NovaConfig.EXTERNAL_INPUT_STEPSIZE_DEGREES

        opcode = self.actionDict[move][self.ACTION_OPERATION_ID_INDEX]
        args = [degrees, 0, 0]
        cmd = (CommandType.INPUT, NovaConstants.MOD_EXTERNAL_INPUT_CONTROL, opcode, args)
        self.move_commands.append(cmd)

    def __onMouse(self, event, x, y, flags, param):
        if event == cv.EVENT_RBUTTONDOWN or event == cv.EVENT_LBUTTONDOWN:
            self.prev_x = x
            self.prev_y = y
            self.mouse_move_on = True
        elif event == cv.EVENT_RBUTTONUP or event == cv.EVENT_LBUTTONUP:
            self.mouse_move_on = False

        if self.mouse_timer.frequencyElapsed(): # trim down the amount of events converted into commands
            if event == cv.EVENT_MOUSEWHEEL:
                self.__calculateMouseWheelMove(flags)
            elif self.mouse_move_on and event == cv.EVENT_MOUSEMOVE:
                self.__calculateMouseMove(x,y,flags)
                self.prev_x = x
                self.prev_y = y

    def __calculateMouseMove(self, x, y, flags):
        mode = self.__determineMouseMode(flags)
        direction_x = self.__determineMouseDirection(x, self.prev_x)
        direction_y = self.__determineMouseDirection(y, self.prev_y)

        # TODO set degrees depending on the delta of X or Y axis (perhaps using multiples of stepsize)
        if not direction_x == '':
            degrees = NovaConfig.EXTERNAL_INPUT_STEPSIZE_DEGREES if direction_x == 'PLUS' else -NovaConfig.EXTERNAL_INPUT_STEPSIZE_DEGREES
            self.__createCommandFromMouseMove(mode, 'X', direction_x, degrees)

        if not direction_y == '':
            degrees = NovaConfig.EXTERNAL_INPUT_STEPSIZE_DEGREES if direction_y == 'PLUS' else -NovaConfig.EXTERNAL_INPUT_STEPSIZE_DEGREES
            self.__createCommandFromMouseMove(mode, 'Y', direction_y, degrees)

    def __determineMouseMode(self, flags):
        mode = ''
        if flags & cv.EVENT_FLAG_LBUTTON:
            mode = 'LBUTTON'
        elif flags & cv.EVENT_FLAG_RBUTTON:
            mode = 'RBUTTON'
        return mode

    def __determineMouseDirection(self, current, previous):
        direction = ''
        if current < previous:
            direction = 'MINUS'
        elif current > previous:
            direction = 'PLUS'
        return direction

    def __createCommandFromMouseMove(self, mode, axis, direction, degrees):
        parts_of_id = ['MOUSE', mode, axis, direction]
        mouse_event_id = '_'.join(parts_of_id)
        move = self.mouse_index[mouse_event_id]

        opcode = self.actionDict[move][self.ACTION_OPERATION_ID_INDEX]
        args = [degrees, 0, 0]
        cmd = (CommandType.INPUT, NovaConstants.MOD_EXTERNAL_INPUT_CONTROL, opcode, args)
        self.move_commands.append(cmd)

    def __calculateMouseWheelMove(self, flags):
        if flags < 0:
            direction = 'PLUS'
        else:
            direction = 'MINUS'

        degrees = NovaConfig.EXTERNAL_INPUT_STEPSIZE_DEGREES if direction == 'PLUS' else -NovaConfig.EXTERNAL_INPUT_STEPSIZE_DEGREES
        move = self.mouse_index['MOUSE_SCROLL_' + direction]
        args = [degrees, 0, 0]
        cmd = (CommandType.INPUT, self.actionDict[move][self.ACTION_OPERATION_ID_INDEX], args)
        self.move_commands.append(cmd)

    def run(self):
        self.__readKeyInput()

    def isRunning(self):
        return self.running

    def commandAvailable(self):
        return len(self.move_commands) > 0

    def readCommand(self):
        return self.move_commands.popleft()
