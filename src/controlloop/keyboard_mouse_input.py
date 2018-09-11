import cv2
from collections import deque
from enum import Enum
from config.constants import NovaConstants

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
        NovaMove.QUIT_CONTROLLER : ('q', 'NONE', 0, "Quit the controller", lambda: __processControllerOperationCommand('QUIT_CONTROLLER')),

        NovaMove.HEAD_MOVE_FRONT : ('e', 'MOUSE_SCROLL_PLUS', 0, "Head movement - forwards", lambda: __processMoveCommand('HEAD_MOVE_FRONT')),
        NovaMove.HEAD_MOVE_BACK : ('d', 'MOUSE_SCROLL_MINUS', 0, "Head movement - backwards", lambda: __processMoveCommand('HEAD_MOVE_BACK')),
        NovaMove.HEAD_MOVE_UP : ('g', 'MOUSE_LBUTTON_Y_PLUS', 0, "Body movement - up", lambda: __processMoveCommand('HEAD_MOVE_UP')),
        NovaMove.HEAD_MOVE_DOWN : ('h', 'MOUSE_LBUTTON_Y_MINUS', 0, "Body movement - down", lambda: __processMoveCommand('HEAD_MOVE_DOWN')),

        NovaMove.BODY_MOVE_RIGHT : ('s', 'MOUSE_LBUTTON_X_MINUS', 0, "Body movement - right", lambda: __processMoveCommand('BODY_MOVE_RIGHT')),
        NovaMove.BODY_MOVE_LEFT : ('f', 'MOUSE_LBUTTON_X_PLUS', 0, "Body movement - left", lambda: __processMoveCommand('BODY_MOVE_LEFT')),

        NovaMove.HEAD_ROTATE_UP : ('i', 'MOUSE_RBUTTON_Y_PLUS', 0, "Head rotation - up", lambda: __processMoveCommand('HEAD_ROTATE_UP')),
        NovaMove.HEAD_ROTATE_DOWN : ('k', 'MOUSE_RBUTTON_Y_MINUS', 0, "Head rotation - down", lambda: __processMoveCommand('HEAD_ROTATE_DOWN')),
        NovaMove.HEAD_ROTATE_LEFT : ('j', 'MOUSE_RBUTTON_X_PLUS', 0, "Head rotation - left", lambda: __processMoveCommand('HEAD_ROTATE_LEFT')),
        NovaMove.HEAD_ROTATE_RIGHT : ('l', 'MOUSE_RBUTTON_X_MINUS', 0, "Head rotation - right", lambda: __processMoveCommand('HEAD_ROTATE_RIGHT')),
    }

    ACTION_KEY_INDEX = 0
    ACTION_MOUSE_INDEX = 1
    ACTION_INT_ID_INDEX = 2
    ACTION_DESCRIPTION_INDEX = 3
    ACTION_ACTION_INDEX = 4

    def __init__(self, serial_communication):
        self.serial_comm = serial_communication
        key_index, mouse_index = self.__buildInputIndex()
        self.key_index = key_index
        self.mouse_index = mouse_index

        self.running = True
        self.move_commands = deque()

        cv2.setMouseCallback(NovaConstants.FACE_DETECTION_WINDOW_NAME, self.__onMouse)
        self.primaryMoveAxes = True

    # build and index of possible keys, dict key as ord('x') so we can search based on the pressed key
    def __buildInputIndex(self):
        key_index = {}
        mouse_index = {}

        for id, tuple in self.actionDict.items():
            (key, mouse, int_id, desc, action) = tuple
            key_index[ord(key)] = id
            mouse_index[mouse] = id

        return key_index, mouse_index

    def __buildMouseIndex(self):
        mouse_index = {}

    def __readKeyInput(self):
        key_pressed = (cv2.waitKey(1) & 0xFF)
        if key_pressed in key_index:
            operation = self.key_index[key_pressed]
            self.actionDict[operation][self.ACTION_ACTION_INDEX]()

    def __processControllerOperationCommand(self, operation):
        if operation == NovaMove.QUIT_CONTROLLER:
            self.running = False

    def __processMoveCommand(self, move):
        cmd = (CommandType.INPUT, actionDict[move][self.ACTION_INT_ID_INDEX])
        self.move_commands.append(move)

    def __onMouse(self, event, x, y, flags, param):
        if event == cv.EVENT_RBUTTONDOWN:
            self.primaryMoveAxes = False

        elif event == cv.EVENT_RBUTTONUP:
            self.primaryMoveAxes = True

        elif event == cv.EVENT_MOUSEWHEEL:
            pass
        elif event == cv.EVENT_MOUSEMOVE:
            pass


    def run(self, cmds):
        self.__readKeyInput()
        self.__readMouseInput()

    def isRunning(self):
        return self.running

    def commandAvailable():
        return len(self.move_commands) > 0

    def getMoveCommand():
        return self.move_commands.popleft()
