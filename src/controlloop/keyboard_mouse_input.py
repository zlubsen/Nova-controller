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

class KeyboardMouseInputLoop:
    # dict that maps defined actions by id to (key_pressed, int_id, description, action) tuples
    actionDict = {
        NovaMove.QUIT_CONTROLLER : ('q', 'NONE', '', "Quit the controller", lambda self: self.__processControllerOperationCommand(NovaMove.QUIT_CONTROLLER)),

        NovaMove.HEAD_MOVE_FRONT : ('e', 'MOUSE_SCROLL_PLUS', NovaConstants.OP_EXTERNAL_INPUT_HEAD_MOVE_FRONT, "Head movement - forwards", lambda self: self.__processMoveCommand(NovaMove.HEAD_MOVE_FRONT)),
        NovaMove.HEAD_MOVE_BACK : ('d', 'MOUSE_SCROLL_MINUS', NovaConstants.OP_EXTERNAL_INPUT_HEAD_MOVE_BACK, "Head movement - backwards", lambda self: self.__processMoveCommand(NovaMove.HEAD_MOVE_BACK)),
        NovaMove.HEAD_MOVE_UP : ('g', 'MOUSE_LBUTTON_Y_PLUS', NovaConstants.OP_EXTERNAL_INPUT_HEAD_MOVE_UP, "Body movement - up", lambda self: self.__processMoveCommand(NovaMove.HEAD_MOVE_UP)),
        NovaMove.HEAD_MOVE_DOWN : ('h', 'MOUSE_LBUTTON_Y_MINUS', NovaConstants.OP_EXTERNAL_INPUT_HEAD_MOVE_DOWN, "Body movement - down", lambda self: self.__processMoveCommand(NovaMove.HEAD_MOVE_DOWN)),

        NovaMove.BODY_MOVE_RIGHT : ('f', 'MOUSE_LBUTTON_X_MINUS', NovaConstants.OP_EXTERNAL_INPUT_BODY_MOVE_RIGHT, "Body movement - right", lambda self: self.__processMoveCommand(NovaMove.BODY_MOVE_RIGHT)),
        NovaMove.BODY_MOVE_LEFT : ('s', 'MOUSE_LBUTTON_X_PLUS', NovaConstants.OP_EXTERNAL_INPUT_BODY_MOVE_LEFT, "Body movement - left", lambda self: self.__processMoveCommand(NovaMove.BODY_MOVE_LEFT)),

        NovaMove.HEAD_ROTATE_UP : ('i', 'MOUSE_RBUTTON_Y_PLUS', NovaConstants.OP_EXTERNAL_INPUT_HEAD_ROTATE_UP, "Head rotation - up", lambda self: self.__processMoveCommand(NovaMove.HEAD_ROTATE_UP)),
        NovaMove.HEAD_ROTATE_DOWN : ('k', 'MOUSE_RBUTTON_Y_MINUS', NovaConstants.OP_EXTERNAL_INPUT_HEAD_ROTATE_DOWN, "Head rotation - down", lambda self: self.__processMoveCommand(NovaMove.HEAD_ROTATE_DOWN)),
        NovaMove.HEAD_ROTATE_LEFT : ('j', 'MOUSE_RBUTTON_X_PLUS', NovaConstants.OP_EXTERNAL_INPUT_HEAD_ROTATE_LEFT, "Head rotation - left", lambda self: self.__processMoveCommand(NovaMove.HEAD_ROTATE_LEFT)),
        NovaMove.HEAD_ROTATE_RIGHT : ('l', 'MOUSE_RBUTTON_X_MINUS', NovaConstants.OP_EXTERNAL_INPUT_HEAD_ROTATE_RIGHT, "Head rotation - right", lambda self: self.__processMoveCommand(NovaMove.HEAD_ROTATE_RIGHT))
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

    # build and index of possible keys, dict key as ord('x') so we can search based on the pressed key
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

    def __processMoveCommand(self, move):
        cmd = (CommandType.INPUT, self.actionDict[move][self.ACTION_OPERATION_ID_INDEX], NovaConfig.EXTERNAL_INPUT_STEPSIZE_DEGREES)
        self.move_commands.append(cmd)

    def __onMouse(self, event, x, y, flags, param):
        #if self.mouse_timer.frequencyElapsed():
        if event == cv.EVENT_RBUTTONDOWN or event == cv.EVENT_LBUTTONDOWN:
            self.prev_x = x
            self.prev_y = y
            self.mouse_move_on = True
        elif event == cv.EVENT_RBUTTONUP or event == cv.EVENT_LBUTTONUP:
            self.mouse_move_on = False
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

        # TODO set degrees depending on the delta of X or Y axis
        if not direction_x == '':
            self.__createCommandFromMouseMove(mode, 'X', direction_x, NovaConfig.EXTERNAL_INPUT_STEPSIZE_DEGREES)

        if not direction_y == '':
            self.__createCommandFromMouseMove(mode, 'Y', direction_y, NovaConfig.EXTERNAL_INPUT_STEPSIZE_DEGREES)

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
        parts = ['MOUSE', mode, axis, direction]
        mouse_event = '_'.join(parts)
        move = self.mouse_index[mouse_event]
        cmd = (CommandType.INPUT, self.actionDict[move][self.ACTION_OPERATION_ID_INDEX], degrees)
        self.move_commands.append(cmd)

    def __calculateMouseWheelMove(self, flags):
        if flags < 0:
            direction = 'PLUS'
        else:
            direction = 'MINUS'

        move = self.mouse_index['MOUSE_SCROLL_' + direction]
        cmd = (CommandType.INPUT, self.actionDict[move][self.ACTION_OPERATION_ID_INDEX], degrees)
        self.move_commands.append(cmd)

    def run(self):
        self.__readKeyInput()

    def isRunning(self):
        return self.running

    def commandAvailable(self):
        return len(self.move_commands) > 0

    def readCommand(self):
        return self.move_commands.popleft()
