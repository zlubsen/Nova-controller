import serial
import sys
from collections import deque
from config.constants import NovaConstants

class Communication:
    def __init__(self):
        self.ser = serial.Serial()
        self.ser.port = self.__determinSerialPort() # TODO only work on windows for now
        self.ser.baudrate = NovaConstants.SERIAL_BAUDRATE
        self.ser.open()

        # for receiving data
        self.recvInProgress = False
        self.newData = False
        self.receivedBytes = []
        self.receivedCommands = deque()

    def close(self):
        self.ser.close()

    def run(self):
        self.__recvBytesWithStartEndMarkers()
        self.__parseInput()

    def commandAvailable(self):
        return len(self.receivedCommands) > 0

    def readCommand(self):
        return self.receivedCommands.popleft()

    def writeCommand(self, modcode, opcode, args):
        cmd_content = [modcode, opcode] + args
        command = NovaConstants.CMD_TEMPLATE.format(*cmd_content)
        self.ser.write(command.encode())
        print("[cntr] " + command)

    def __recvBytesWithStartEndMarkers(self):
        while(self.ser.in_waiting > 0 and not self.newData):
            receivedByte = self.ser.read()

            if self.recvInProgress:
                if receivedByte is not NovaConstants.CMD_END_MARKER.encode():
                    self.receivedBytes.append(receivedByte)
                else:
                    self.recvInProgress = False
                    self.newData = True
            elif receivedByte is NovaConstants.CMD_START_MARKER.encode():
                self.recvInProgress = True

    def __parseInput(self):
        if self.newData:
            cmdFields = ''.join([byte.decode() for byte in self.receivedBytes]).split(NovaConstants.CMD_SEPARATOR)
            self.receivedCommands.append(tuple(cmdFields))
            self.newData = False
            self.receivedBytes.clear()
            self.__printReceivedCommand(tuple(cmdFields))

    def __printReceivedCommand(self, command):
        print("[nova] " + ':'.join(command))

    def __determinSerialPort(self):
        if sys.platform.startswith('win32'):
            return NovaConstants.SERIAL_PORT_WINDOWS
        elif sys.platform.startswith('darwin'):
            return NovaConstants.SERIAL_PORT_MACOS
        elif sys.platform.startswith('linux'):
            return NovaConstants.SERIAL_PORT_LINUX
