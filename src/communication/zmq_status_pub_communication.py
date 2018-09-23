import zmq
from decimal import Decimal
from config.constants import NovaConstants
from utils.frequencytimer import FrequencyTimer
from utils.commandtype_enum import CommandType

class StatusPubCommunication:
    # index ids must match the codes in the Nova-platform constants
    # TODO SET_MODE constant is now somewhere in the middel ('9'), which is ugly
    assetDict = {
        NovaConstants.OP_STATUS_RECEIVE_SERVO_1:"servo1",
        NovaConstants.OP_STATUS_RECEIVE_SERVO_2:"servo2",
        '3':"servo3",
        '4':"servo4",
        '5':"servo5",
        '6':"ultrasound",
        '7':"joy_left",
        '8':"joy_right",
        '10':"pid_distance_avoid",
        '11':"pid_x_face_detection",
        '12':"pid_y_face_detection"
    }

    def __init__(self, status_dict, uri="tcp://*:5556", pub_frequency=1000):
        self.__setupZMQ(uri)
        self.timer = FrequencyTimer(pub_frequency)
        self.assetStatus = {}

        self.status_dict = status_dict

#    def __initAssets(self):
#        for k,v in StatusPubCommunication.assetDict:
#            self.assetStatus.add()

    def __setupZMQ(self, uri):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(uri)

    def __processStatusUpdates(self, cmds):
        for cmd in cmds:
            if cmd[0] == CommandType.NOVA:
                (type, modcode, opcode, arg1, arg2, arg3) = cmd
                if modcode is NovaConstants.MOD_STATUS_NOVA:
                    self.__updateStatus(StatusPubCommunication.assetDict[opcode],(arg1,arg2,arg3))

                    #TODO separate receiving status updates and sending them via MQ; status is also needed in the controller
                    if opcode in [NovaConstants.OP_STATUS_RECEIVE_DISTANCE_PID,
                                    NovaConstants.OP_STATUS_RECEIVE_FACEDETECT_PID_X,
                                    NovaConstants.OP_STATUS_RECEIVE_FACEDETECT_PID_Y]:
                        if opcode == NovaConstants.OP_STATUS_RECEIVE_DISTANCE_PID:
                            key_modcode = NovaConstants.MOD_DISTANCE_AVOIDANCE
                            key_opcode = NovaConstants.OP_DISTANCE_SET_PID_TUNING
                        elif opcode == NovaConstants.OP_STATUS_RECEIVE_FACEDETECT_PID_X:
                            key_modcode = NovaConstants.MOD_FACE_DETECTION
                            key_opcode = NovaConstants.OP_FACE_DETECTION_SET_X_PID_TUNING
                        elif opcode == NovaConstants.OP_STATUS_RECEIVE_FACEDETECT_PID_Y:
                            key_modcode = NovaConstants.MOD_FACE_DETECTION
                            key_opcode = NovaConstants.OP_FACE_DETECTION_SET_Y_PID_TUNING

                        self.status_dict[f"{key_modcode}_{key_opcode}_Kp"] = Decimal(arg1)/1000
                        self.status_dict[f"{key_modcode}_{key_opcode}_Ki"] = Decimal(arg2)/1000
                        self.status_dict[f"{key_modcode}_{key_opcode}_Kd"] = Decimal(arg3)/1000

                    cmds.remove(cmd)

    def __updateStatus(self, asset, status):
        self.assetStatus[asset] = status

    def __publishStatuses(self):
        self.socket.send_pyobj(self.assetStatus)

    def run(self, cmds):
        self.__processStatusUpdates(cmds)

        if self.timer.frequencyElapsed():
            self.__publishStatuses()

    def cleanup(self):
        self.socket.close()
        self.context.term()
