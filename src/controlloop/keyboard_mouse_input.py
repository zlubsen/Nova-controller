import cv2 as cv
from collections import deque
from enum import Enum
from decimal import Decimal
from communication.protocol import mapPIDNodes
from communication.protocol import createCommand
from config.config import NovaConfig
from utils.commandtype_enum import CommandType
from utils.frequencytimer import FrequencyTimer

class NovaMove(Enum):
    HEAD_MOVE_FRONT = 1
    HEAD_MOVE_BACK = 2
    HEAD_MOVE_UP = 3
    HEAD_MOVE_DOWN = 4
    BODY_MOVE_RIGHT = 5
    BODY_MOVE_LEFT = 6
    HEAD_ROTATE_UP = 7
    HEAD_ROTATE_DOWN = 8
    HEAD_ROTATE_LEFT = 9
    HEAD_ROTATE_RIGHT = 10
    SET_MODE_JOYSTICK_ABSOLUTE = 11
    SET_MODE_JOYSTICK_RELATIVE = 12
    SET_MODE_EXTERNAL_INPUT = 13
    SET_MODE_DISTANCE_AVOIDANCE = 14
    SET_MODE_FACE_DETECTION = 15
    QUIT_CONTROLLER = 16
    TOGGLE_WINDOW_FULL_SCREEN = 17
    TOGGLE_DISPLAY_CONTROLS = 18
    TOGGLE_STATUS_DETAILS = 19
    TUNE_CYCLE_PID_CONTROLLER_IN_MODULE = 20
    TOGGLE_PID_MANUAL_AUTO = 21
    TUNE_PID_P_VALUE_UP = 22
    TUNE_PID_P_VALUE_DOWN = 23
    TUNE_PID_I_VALUE_UP = 24
    TUNE_PID_I_VALUE_DOWN = 25
    TUNE_PID_D_VALUE_UP = 26
    TUNE_PID_D_VALUE_DOWN = 27

class KeyboardMouseInputLoop:
    # dict that maps defined actions by id to (key_binding, mouse_binding, protocol_id, description, action) tuples
    actionDict = {
        NovaMove.QUIT_CONTROLLER : ('q', 'NONE', '', "Quit the controller", lambda self: self.__processQuitControllerCommand()),
        NovaMove.TOGGLE_WINDOW_FULL_SCREEN : ('c', 'NONE', '', "Toggle full screen", lambda self: self.__processToggleWindowFullScreenCommand()),
        NovaMove.TOGGLE_DISPLAY_CONTROLS : ('z', 'NONE', '', "Show/Hide controls on screen", lambda self: self.__processToggleDisplayControlsCommand()),
        NovaMove.TOGGLE_STATUS_DETAILS : ('x', 'NONE', '', "Show/Hide Nova status on screen", lambda self: self.__processToggleDisplayStatusDetailsCommand()),

        NovaMove.SET_MODE_JOYSTICK_ABSOLUTE : ('1', 'NONE', "joystick_absolute", "Set mode to Joystick - absolute control", lambda self: self.__processModeSelectionCommand(NovaMove.SET_MODE_JOYSTICK_ABSOLUTE)),
        NovaMove.SET_MODE_JOYSTICK_RELATIVE : ('2', 'NONE', "joystick_relative", "Set mode to Joystick - relative control", lambda self: self.__processModeSelectionCommand(NovaMove.SET_MODE_JOYSTICK_RELATIVE)),
        NovaMove.SET_MODE_EXTERNAL_INPUT : ('3', 'NONE', "external_input", "Set mode to External input (keyboard, mouse, API)", lambda self: self.__processModeSelectionCommand(NovaMove.SET_MODE_EXTERNAL_INPUT)),
        NovaMove.SET_MODE_DISTANCE_AVOIDANCE : ('4', 'NONE', "keep_distance", "Set mode to Distance Avoid", lambda self: self.__processModeSelectionCommand(NovaMove.SET_MODE_DISTANCE_AVOIDANCE)),
        NovaMove.SET_MODE_FACE_DETECTION : ('5', 'NONE', "track_object", "Set mode to Face Detection", lambda self: self.__processModeSelectionCommand(NovaMove.SET_MODE_FACE_DETECTION)),

        NovaMove.HEAD_MOVE_FRONT : ('e', 'MOUSE_SCROLL_PLUS', "servo1", "Head movement - forwards", lambda self: self.__processMoveCommand(NovaMove.HEAD_MOVE_FRONT, True)),
        NovaMove.HEAD_MOVE_BACK : ('d', 'MOUSE_SCROLL_MINUS', "servo1", "Head movement - backwards", lambda self: self.__processMoveCommand(NovaMove.HEAD_MOVE_BACK, False)),
        NovaMove.HEAD_MOVE_UP : ('g', 'MOUSE_LBUTTON_Y_PLUS', "servo5", "Head movement - up", lambda self: self.__processMoveCommand(NovaMove.HEAD_MOVE_UP, True)),
        NovaMove.HEAD_MOVE_DOWN : ('h', 'MOUSE_LBUTTON_Y_MINUS', "servo5", "Head movement - down", lambda self: self.__processMoveCommand(NovaMove.HEAD_MOVE_DOWN, False)),

        NovaMove.BODY_MOVE_RIGHT : ('f', 'MOUSE_LBUTTON_X_MINUS', "servo4", "Body movement - right", lambda self: self.__processMoveCommand(NovaMove.BODY_MOVE_RIGHT, True)),
        NovaMove.BODY_MOVE_LEFT : ('s', 'MOUSE_LBUTTON_X_PLUS', "servo4", "Body movement - left", lambda self: self.__processMoveCommand(NovaMove.BODY_MOVE_LEFT, False)),

        NovaMove.HEAD_ROTATE_UP : ('i', 'MOUSE_RBUTTON_Y_PLUS', "servo3", "Head rotation - up", lambda self: self.__processMoveCommand(NovaMove.HEAD_ROTATE_UP, True)),
        NovaMove.HEAD_ROTATE_DOWN : ('k', 'MOUSE_RBUTTON_Y_MINUS', "servo3", "Head rotation - down", lambda self: self.__processMoveCommand(NovaMove.HEAD_ROTATE_DOWN, False)),
        NovaMove.HEAD_ROTATE_LEFT : ('j', 'MOUSE_RBUTTON_X_PLUS', "servo2", "Head rotation - left", lambda self: self.__processMoveCommand(NovaMove.HEAD_ROTATE_LEFT, True)),
        NovaMove.HEAD_ROTATE_RIGHT : ('l', 'MOUSE_RBUTTON_X_MINUS', "servo2", "Head rotation - right", lambda self: self.__processMoveCommand(NovaMove.HEAD_ROTATE_RIGHT, False)),

        NovaMove.TUNE_PID_P_VALUE_UP : ('p', 'NONE', None, "Tune PID - increase Kp", lambda self: self.__processTunePIDCommand(NovaMove.TUNE_PID_P_VALUE_UP)),
        NovaMove.TUNE_PID_P_VALUE_DOWN : (';', 'NONE', None, "Tune PID - decrease Kp", lambda self: self.__processTunePIDCommand(NovaMove.TUNE_PID_P_VALUE_DOWN)),
        NovaMove.TUNE_PID_I_VALUE_UP : ('[', 'NONE', None, "Tune PID - increase Ki", lambda self: self.__processTunePIDCommand(NovaMove.TUNE_PID_I_VALUE_UP)),
        NovaMove.TUNE_PID_I_VALUE_DOWN : ('\'', 'NONE', None, "Tune PID - decrease Ki", lambda self: self.__processTunePIDCommand(NovaMove.TUNE_PID_I_VALUE_DOWN)),
        NovaMove.TUNE_PID_D_VALUE_UP : (']', 'NONE', None, "Tune PID - increase Kd", lambda self: self.__processTunePIDCommand(NovaMove.TUNE_PID_D_VALUE_UP)),
        NovaMove.TUNE_PID_D_VALUE_DOWN : ('\\', 'NONE', None, "Tune PID - decrease Kd", lambda self: self.__processTunePIDCommand(NovaMove.TUNE_PID_D_VALUE_DOWN)),
        NovaMove.TUNE_CYCLE_PID_CONTROLLER_IN_MODULE : ('0', 'NONE', None, "Tune PID - Cycle PID within module", lambda self: self.__processTunePIDCommand(NovaMove.TUNE_CYCLE_PID_CONTROLLER_IN_MODULE)),
        NovaMove.TOGGLE_PID_MANUAL_AUTO : ('-', 'NONE', None, "Tune PID - Toggle current on/off", lambda self: self.__processTunePIDCommand(NovaMove.TOGGLE_PID_MANUAL_AUTO)),
    }

    ACTION_KEY_INDEX = 0
    ACTION_MOUSE_INDEX = 1
    ACTION_OPERATION_ID_INDEX = 2
    ACTION_DESCRIPTION_INDEX = 3
    ACTION_LAMBDA_INDEX = 4

    THREEPLACES = Decimal(10) ** -3
    pid_tune_stepsize = Decimal(NovaConfig.TUNE_PID_STEPSIZE).quantize(THREEPLACES)

    def __init__(self, serial_communication, status_dict):
        self.serial_comm = serial_communication
        self.status_dict = status_dict

        self.__buildInputIndexes()
        self.__buildPIDIndex()

        self.running = True
        self.move_commands = deque()

        self.__setupMouseControl()
        self.__setupFrameDecoration()

    # build and index of possible keys/mouse events, (dict key as ord('x')) so we can search based on the pressed key and mouse event
    def __buildInputIndexes(self):
        key_index = {}
        mouse_index = {}

        for id, items in self.actionDict.items():
            (key, mouse, op_id, desc, action) = items
            key_index[ord(key)] = id
            mouse_index[mouse] = id

        self.key_index = key_index
        self.mouse_index = mouse_index

    def __buildMouseIndex(self):
        mouse_index = {}

    def __buildPIDIndex(self):
        self.pid_index = mapPIDNodes()
        for k,v in self.pid_index.items():
            self.__setCurrentPIDindex(k,0)

    def __setupMouseControl(self):
        self.mouse_move_on = False
        cv.setMouseCallback(NovaConfig.NOVA_WINDOW_NAME, self.__onMouse)
        self.mouse_timer = FrequencyTimer(NovaConfig.EXTERNAL_INPUT_MOUSE_FREQUENCY_MS)

    def __setupFrameDecoration(self):
        self.show_controls = False
        self.help_text_keys = self.__buildHelpTextForKeys()
        self.show_status = False

    def __buildHelpTextForKeys(self):
        help_text_keys = []
        for id, items in self.actionDict.items():
            key = items[0]
            text = items[3]
            help_text_keys.append(f"{key} : {text}")

        return help_text_keys

    def __readKeyInput(self):
        key_pressed = (cv.waitKey(1) & 0xFF)
        if key_pressed in self.key_index:
            operation = self.key_index[key_pressed]
            self.actionDict[operation][self.ACTION_LAMBDA_INDEX](self)

    def __processQuitControllerCommand(self):
        self.running = False
        print("[cntr] Closing Nova controller... Bye")

    def __processToggleDisplayControlsCommand(self):
        self.show_controls = not self.show_controls

    def __processToggleDisplayStatusDetailsCommand(self):
        self.show_status = not self.show_status

    def __processToggleWindowFullScreenCommand(self):
        window_mode = int(cv.getWindowProperty(NovaConfig.NOVA_WINDOW_NAME, cv.WND_PROP_FULLSCREEN))
        if window_mode == cv.WINDOW_FULLSCREEN:
            cv.setWindowProperty(NovaConfig.NOVA_WINDOW_NAME, cv.WND_PROP_FULLSCREEN, cv.WINDOW_NORMAL)
        else:
            cv.setWindowProperty(NovaConfig.NOVA_WINDOW_NAME, cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

    def __processModeSelectionCommand(self, operation):
        new_module = self.actionDict[operation][self.ACTION_OPERATION_ID_INDEX]
        if new_module != self.status_dict["current_mode"]:
            cmd = [CommandType.INPUT] + createCommand().setModule("nova").setOperation("set_mode").setModeArg(new_module).build()
            self.move_commands.append(cmd)
            self.status_dict["current_mode"] = new_module

    def __processMoveCommand(self, move, positive_direction):
        degrees = NovaConfig.EXTERNAL_INPUT_STEPSIZE_DEGREES if positive_direction else -NovaConfig.EXTERNAL_INPUT_STEPSIZE_DEGREES

        asset = self.actionDict[move][self.ACTION_OPERATION_ID_INDEX]
        args = [degrees]
        cmd = [CommandType.INPUT] + createCommand().setModule("external_input").setAsset(asset).setOperation("set_degree_steps").setArgs(args).build()
        self.move_commands.append(cmd)

    def __processTunePIDCommand(self, move):
        module = self.status_dict["current_mode"]
        if move == NovaMove.TUNE_CYCLE_PID_CONTROLLER_IN_MODULE:
            self.__togglePIDcontrollerToTune(module)
        elif move == NovaMove.TOGGLE_PID_MANUAL_AUTO:
            self.__togglePIDcontrollerOnOff(module)
        else: # actual tuning of pid settings (up | down)
            asset = self.__determinePIDasset(module)
            pid_values = self.__determinePIDvalues(move, module, asset)
            args = list(int(x*1000) for x in pid_values) # nova command protocol allows only to send INTs
            cmd = [CommandType.INPUT] + createCommand().setModule(module).setAsset(asset).setOperation("set_tuning").setArgs(args).build()
            self.move_commands.append(cmd)

    def __togglePIDcontrollerToTune(self, module):
        if module in self.pid_index:
            current_index = self.__getCurrentPIDindex(module)
            no_of_module_pids = len(self.pid_index[module])
            new_index = current_index+1
            if new_index >= no_of_module_pids:
                new_index = 0
            self.__setCurrentPIDindex(module, new_index)
            asset = self.__determinePIDasset(module)
            print(f"[ctrl] Now tuning PID {asset} for module {module}")

    def __togglePIDcontrollerOnOff(self, module):
        if module in self.pid_index:
            asset = self.__determinePIDasset(module)
            print(f"Toggled PID controller {asset} for module {module} auto/manual")
            cmd = [CommandType.INPUT] + createCommand().setModule(module).setAsset(asset).setOperation("toggle_auto").build()
            self.move_commands.append(cmd)

    def __determinePIDasset(self, module):
        index = self.__getCurrentPIDindex(module)
        assets = self.pid_index[module]
        return assets[index]

    def __getCurrentPIDindex(self, module):
        key = f"current_pid_controller_index_{module}"
        return self.status_dict[key]

    def __setCurrentPIDindex(self, module, index):
        key = f"current_pid_controller_index_{module}"
        self.status_dict[key] = index

    # TODO can we make this one more neat?
    def __determinePIDvalues(self, move, module, asset):
        Kp = self.status_dict[f"{module}_{asset}_Kp"]
        Ki = self.status_dict[f"{module}_{asset}_Ki"]
        Kd = self.status_dict[f"{module}_{asset}_Kd"]

        if move == NovaMove.TUNE_PID_P_VALUE_UP:
            Kp = Kp + self.pid_tune_stepsize
        elif move == NovaMove.TUNE_PID_P_VALUE_DOWN:
            Kp = Kp - self.pid_tune_stepsize
        elif move == NovaMove.TUNE_PID_I_VALUE_UP:
            Ki = Ki + self.pid_tune_stepsize
        elif move == NovaMove.TUNE_PID_I_VALUE_DOWN:
            Ki = Ki - self.pid_tune_stepsize
        elif move == NovaMove.TUNE_PID_D_VALUE_UP:
            Kd = Kd + self.pid_tune_stepsize
        elif move == NovaMove.TUNE_PID_D_VALUE_DOWN:
            Kd = Kd - self.pid_tune_stepsize

        Kp_final, Ki_final, Kd_final = self.__sanitizeValues(Kp, Ki, Kd)

        self.status_dict[f"{module}_{asset}_Kp"] = Kp_final
        self.status_dict[f"{module}_{asset}_Ki"] = Ki_final
        self.status_dict[f"{module}_{asset}_Kd"] = Kd_final

        return (Kp_final, Ki_final, Kd_final)

    def __sanitizeValues(self, Kp, Ki, Kd):
        if Kp <= 0:
            Kp = Decimal(0)
        if Ki <= 0:
            Ki = Decimal(0)
        if Kd <= 0:
            Kd = Decimal(0)

        return (Decimal(Kp).quantize(self.THREEPLACES), Decimal(Ki).quantize(self.THREEPLACES), Decimal(Kd).quantize(self.THREEPLACES))

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
        mouse_mode = self.__determineMouseMode(flags)
        direction_x = self.__determineMouseDirection(x, self.prev_x)
        direction_y = self.__determineMouseDirection(y, self.prev_y)

        # TODO set degrees depending on the delta of X or Y axis (perhaps using multiples of stepsize)
        if not direction_x == '':
            degrees = NovaConfig.EXTERNAL_INPUT_STEPSIZE_DEGREES if direction_x == 'PLUS' else -NovaConfig.EXTERNAL_INPUT_STEPSIZE_DEGREES
            self.__createCommandFromMouseMove(mouse_mode, 'X', direction_x, degrees)

        if not direction_y == '':
            degrees = NovaConfig.EXTERNAL_INPUT_STEPSIZE_DEGREES if direction_y == 'PLUS' else -NovaConfig.EXTERNAL_INPUT_STEPSIZE_DEGREES
            self.__createCommandFromMouseMove(mouse_mode, 'Y', direction_y, degrees)

    def __determineMouseMode(self, flags):
        mode = ''
        if flags & cv.EVENT_FLAG_LBUTTON or flags & cv.EVENT_FLAG_CTRLKEY:
            mode = 'LBUTTON'
        elif flags & cv.EVENT_FLAG_RBUTTON or flags & cv.EVENT_FLAG_SHIFTKEY:
            mode = 'RBUTTON'
        return mode

    def __determineMouseDirection(self, current, previous):
        direction = ''
        if current < previous:
            direction = 'MINUS'
        elif current > previous:
            direction = 'PLUS'
        return direction

    def __createCommandFromMouseMove(self, mouse_mode, axis, direction, degrees):
        parts_of_id = ['MOUSE', mouse_mode, axis, direction]
        mouse_event_id = '_'.join(parts_of_id)
        move = self.mouse_index[mouse_event_id]

        asset = self.actionDict[move][self.ACTION_OPERATION_ID_INDEX]
        args = [degrees]
        cmd = [CommandType.INPUT] + createCommand().setModule("external_input").setAsset(asset).setOperation("set_degree_steps").setArgs(args).build()
        self.move_commands.append(cmd)

    def __calculateMouseWheelMove(self, flags):
        if flags < 0:
            direction = 'PLUS'
        else:
            direction = 'MINUS'

        degrees = NovaConfig.EXTERNAL_INPUT_STEPSIZE_DEGREES if direction == 'PLUS' else -NovaConfig.EXTERNAL_INPUT_STEPSIZE_DEGREES
        move = self.mouse_index['MOUSE_SCROLL_' + direction]
        asset = self.actionDict[move][self.ACTION_OPERATION_ID_INDEX]
        args = [degrees]
        cmd = [CommandType.INPUT] + createCommand().setModule("external_input").setAsset(asset).setOperation("set_degree_steps").setArgs(args).build()
        self.move_commands.append(cmd)

    # TODO lots of config items to put in NovaConfig here
    def __decorateFrame(self, frame):
        if self.show_controls:
            index = 0
            for line in self.help_text_keys:
                x_coordinate = 5
                y_coordinate = 10 + (12 * (index))
                cv.putText(frame, line, (x_coordinate, y_coordinate), cv.FONT_HERSHEY_PLAIN, 0.75, (255,255,255), thickness = 1)
                index += 1
        if self.show_status:
            # TODO placeholder text and position. Perhaps move this whole function to another class...
            cv.putText(frame, "Here comes status stuff...", (200, 180), cv.FONT_HERSHEY_PLAIN, 0.75, (255,255,255), thickness = 1)

    def run(self):
        self.__readKeyInput()
        frame = self.status_dict["frame"]
        self.__decorateFrame(frame)

    def isRunning(self):
        return self.running

    def commandAvailable(self):
        return len(self.move_commands) > 0

    def readCommand(self):
        return self.move_commands.popleft()
