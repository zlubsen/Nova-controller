from utils.commandtype_enum import CommandType

class KeyboardMouseControlLoop(serial_comm):
    def __init__(self, serial_communication):
        self.serial_comm = serial_communication

    def __processCommand():

    def run(cmds):
        for cmd in cmds:
            if cmd[0] == CommandType.INPUT:
                (type, ...) = cmd
