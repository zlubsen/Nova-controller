# from util....timer import FrequencyTimer

assetDict = {
    1:"servo1",
    2:"servo2",
    3:"servo3",
    4:"servo4",
    5:"servo5",
    6:"uss",
    7:"joy_left"
    8:"joy_right"
}

class StatusPublishControlLoop:
    def __init__(self, ser_comm, pub_socket):
        self.comm = ser_comm
        self.socket = pub_socket
        self.assetStatus = {}
        #self.timer = FrequencyTimer()

    def __processResponses(self, cmds):
        for cmd in cmds:
            (modcode, opcode, arg1, arg2, arg3) = cmd
            if modcode is NovaConstants.MOD_STATUS_NOVA:
                self.__storeStatus(assetDict[opcode],(arg1,arg2,arg3))

    def __storeStatus(self, asset, status):
        self.assetStatus[asset] = status

    def __publishStatuses():
        self.socket.send_pyobj(self.assetStatus)

    def run(cmds):
        self.__processResponses(cmds)

        # if self.timer.frequencyElapsed():
        #   self.__publishStatuses()
