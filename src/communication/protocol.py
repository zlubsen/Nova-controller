class GenericProtocalElement:
    operations = {}

    assets = {}

    def __init__(self, id, code):
        self.id = id
        self.code = code

    def operation(self, op_name):
        if op_name in self.operations:
            return self.operations[op_name]
        else:
            return '0'

class ServoAsset(GenericProtocalElement):
    operations = {
        "get_degree" : '1',
        "set_degree" : '2',
        "set_degree_steps" : '3'
    }

    def __init__(self, id, code):
        super().__init__(id, code)

class UltraSoundAsset(GenericProtocalElement):
    operations = {
        "get_distance" : '1'
    }

    def __init__(self, id, code):
        super().__init__(id, code)

class PIDAsset(GenericProtocalElement):
    operations = {
        "toggle_auto" : '1',
        "set_setpoint" : '2',
        "set_tuning" : '3',
        "get_tuning" : '4'
    }

    def __init__(self, id, code):
        super().__init__(id, code)

class NovaModule(GenericProtocalElement):
    operations = {
        "set_mode" : '1'
    }

    assets = {
        "module" : GenericProtocalElement("module", '0'),
        "servo1" : ServoAsset("servo1", '1'),
        "servo2" : ServoAsset("servo2", '2'),
        "servo3" : ServoAsset("servo3", '3'),
        "servo4" : ServoAsset("servo4", '4'),
        "servo5" : ServoAsset("servo5", '5'),
        "ultrasound" : UltraSoundAsset("ultrasound", '6')
    }

    def __init__(self, id, code):
        super().__init__(id, code)

class ExternalInputModule(GenericProtocalElement):
    operations = {}

    assets = {
        "servo1" : ServoAsset("servo1", '1'),
        "servo2" : ServoAsset("servo2", '2'),
        "servo3" : ServoAsset("servo3", '3'),
        "servo4" : ServoAsset("servo4", '4'),
        "servo5" : ServoAsset("servo5", '5')
    }

    def __init__(self, id, code):
        super().__init__(id, code)

class KeepDistanceModule(GenericProtocalElement):
    operations = {
        "set_min_distance" : '1',
        "set_max_distance" : '2'
    }

    assets = {
        "module" : GenericProtocalElement("module", '0'),
        "pid" : PIDAsset("pid", '1')
    }

    def __init__(self, id, code):
        super().__init__(id, code)

class TrackObjectModule(GenericProtocalElement):
    operations = {
        "set_coordinates" : '1',
        "ack_coordinates" : '2'
    }

    assets = {
        "module" : GenericProtocalElement("module", '0'),
        "pid_x" : PIDAsset("pid_x", '1'),
        "pid_y" : PIDAsset("pid_y", '2')
    }

    def __init__(self, id, code):
        super().__init__(id, code)

class NovaProtocolCommandBuilder:

    modules = {
        "nova" : NovaModule("nova", '0'),
        "joystick_absolute" : GenericProtocalElement("joystick_absolute", '1'),
        "joystick_relative" : GenericProtocalElement("joystick_relative", '2'),
        "external_input" : ExternalInputModule("external_input", '3'),
        "keep_distance" : KeepDistanceModule("keep_distance", '4'),
        "track_object" : TrackObjectModule("track_object", '5')
    }

    def __init__(self):
        self.module = None
        self.asset = None
        self.operation = None
        self.args = []

    def setModule(self, mod_name):
        if mod_name in self.modules:
            self.module = self.modules[mod_name]

        return self

    def setAsset(self, asset_name):
        if not self.module == None:
            if asset_name in self.module.assets:
                self.asset = self.module.assets[asset_name]

        return self

    def setOperation(self, op_name):
        if not self.module == None:
            if not self.asset == None:
                if self.asset.id != "module":
                    if op_name in self.asset.operations:
                        self.operation = self.asset.operation(op_name)
                else:
                    if op_name in self.module.operations:
                        self.operation = self.module.operation(op_name)
            else:
                self.setAsset("module")
                self.setOperation(op_name)


        return self

    def setArgs(self, args_list):
        self.args = args_list

        return self

    def setModuleArg(self, module_name):
        self.args.append(self.modules[module_name].code)

    def build(self):
        assert self.module != None
        assert self.asset != None
        assert self.operation != None

        return [self.module.code,
            self.asset.code,
            self.operation,
            str(len(self.args))] + self.args

def createCommand():
    return NovaProtocolCommandBuilder()
