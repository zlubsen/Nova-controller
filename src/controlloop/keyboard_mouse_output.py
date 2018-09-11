from utils.commandtype_enum import CommandType

class KeyboardMouseControlLoop():
    def __init__(self, serial_communication):
        self.serial_comm = serial_communication

    def __processCommand(self):
        pass

    def run(self, cmds):
        for cmd in cmds:
            if cmd[0] == CommandType.INPUT:
                pass
                #(type, ...) = cmd

    def cleanup(self):
        pass
