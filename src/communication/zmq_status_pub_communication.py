import zmq
from config.constants import NovaConstants
from utils.frequencytimer import FrequencyTimer
from utils.commandtype_enum import CommandType

class StatusPubCommunication:
    # index ids must match the codes in the Nova-platform constants
    assetDict = {
        '1':"servo1",
        '2':"servo2",
        '3':"servo3",
        '4':"servo4",
        '5':"servo5",
        '6':"ultrasound",
        '7':"joy_left",
        '8':"joy_right"
    }

    def __init__(self, uri="tcp://*:5556", pub_frequency=1000):
        self.__setupZMQ(uri)
        self.timer = FrequencyTimer(pub_frequency)
        self.assetStatus = {}

    def __initAssets(self):
        for k,v in StatusPubCommunication.assetDict:
            self.assetStatus.add()

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
                    cmds.remove(cmd)

    def __updateStatus(self, asset, status):
        self.assetStatus[asset] = status

    def __publishStatuses(self):
        self.socket.send_pyobj(self.assetStatus)

    def run(self, cmds, frame):
        self.__processStatusUpdates(cmds)

        if self.timer.frequencyElapsed():
            self.__publishStatuses()

    def cleanup(self):
        self.socket.close()
        self.context.term()
