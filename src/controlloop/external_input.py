from config.constants import NovaConstants
from utils.commandtype_enum import CommandType

class ExternalInputControlLoop():
    def __init__(self, serial_communication):
        self.serial_comm = serial_communication

    def __processCommand(self):
        pass

    def run(self, cmds):
        for cmd in cmds:
            if cmd[0] == CommandType.INPUT:
                (type, opcode, degrees) = cmd
                self.serial_comm.writeCommand(NovaConstants.MOD_EXTERNAL_INPUT_CONTROL, opcode, [degrees])

    def cleanup(self):
        pass
