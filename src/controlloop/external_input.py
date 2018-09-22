from config.constants import NovaConstants
from utils.commandtype_enum import CommandType

class ExternalInputControlLoop():
    def __init__(self, serial_communication, status_dict):
        self.serial_comm = serial_communication
        self.status_dict = status_dict

    def __processCommand(self):
        pass

    def run(self, cmds):
        for cmd in cmds:
            if cmd[0] == CommandType.INPUT:
                (type, modcode, opcode, args) = cmd
                self.serial_comm.writeCommand(modcode, opcode, args)
                cmds.remove(cmd)

    def cleanup(self):
        pass
