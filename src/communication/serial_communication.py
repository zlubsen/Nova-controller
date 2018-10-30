import serial
import sys
from collections import deque
from config.constants import NovaConstants
from config.config import NovaConfig
from utils.commandtype_enum import CommandType
from utils.frequencytimer import FrequencyTimer
from communication.protocol import NovaProtocolCommandReader

class SerialCommunication:
    def __init__(self):
        self.connection_timer = FrequencyTimer(NovaConfig.SERIAL_RECONNECT_MS)
        self.ser = serial.Serial()
        self.ser.port = self.__determineSerialPort() # TODO only work on windows for now
        self.ser.baudrate = NovaConfig.SERIAL_BAUDRATE
        self.__open()

        # for receiving data
        self.recvInProgress = False
        self.newData = False
        self.receivedBytes = []
        self.receivedCommands = deque()

        self.protocolReader = NovaProtocolCommandReader()

    def __open(self):
        try:
            self.ser.open()
            self.connected = True
        except serial.serialutil.SerialException:
            self.connected = False
            print("[cntr] Failed to open serial connection to Nova.")

    def close(self):
        self.ser.close()

    def run(self):
        if self.connected:
            self.__recvBytesWithStartEndMarkers()
            self.__parseInput()
        elif self.connection_timer.frequencyElapsed():
            self.__open()

    def commandAvailable(self):
        return len(self.receivedCommands) > 0

    def readCommand(self):
        return self.receivedCommands.popleft()

    def writeCommand(self, cmd_list_codes):
        cmd_list_strings = [str(i) for i in cmd_list_codes]
        command = NovaConstants.CMD_START_MARKER + NovaConstants.CMD_SEPARATOR.join(cmd_list_strings) + NovaConstants.CMD_END_MARKER
        if self.connected:
            try:
                self.ser.write(command.encode())
                self.__printOutgoingCommand(command)
            except serial.serialutil.SerialException:
                self.connected = False
                print("[ctrl] SerialException while writing to Nova.")

    def __recvBytesWithStartEndMarkers(self):
        try:
            while(self.connected and self.ser.in_waiting > 0 and not self.newData):
                receivedByte = self.ser.read()

                if self.recvInProgress:
                    if receivedByte is not NovaConstants.CMD_END_MARKER.encode():
                        self.receivedBytes.append(receivedByte)
                    else:
                        self.recvInProgress = False
                        self.newData = True
                elif receivedByte is NovaConstants.CMD_START_MARKER.encode():
                    self.recvInProgress = True
        except serial.serialutil.SerialException:
            self.connected = False
            self.newData = False
            self.recvInProgress = False
            self.receivedBytes = []
            print("[ctrl] SerialException while reading from Nova.")

    def __parseInput(self):
        if self.newData:
            cmdFields = ''.join([byte.decode() for byte in self.receivedBytes]).split(NovaConstants.CMD_SEPARATOR)
            cmd = [CommandType.NOVA] + self.protocolReader.readCommand(cmdFields)
            self.newData = False
            self.receivedBytes.clear()
            self.receivedCommands.append(tuple(cmd))
            self.__printIncomingCommand(cmd)

    def __printIncomingCommand(self, command):
        command[0] = str(command[0])
        print("[nova] " + ':'.join(command))

    def __printOutgoingCommand(self, command):
        print("[cntr] " + command)

    def __determineSerialPort(self):
        if sys.platform.startswith('win32'):
            return NovaConfig.SERIAL_PORT_WINDOWS
        elif sys.platform.startswith('darwin'):
            return NovaConfig.SERIAL_PORT_MACOS
        elif sys.platform.startswith('linux'):
            return NovaConfig.SERIAL_PORT_LINUX
