from utils.commandtype_enum import CommandType

class ProtocolNode:
    def __init__(self, id, code):
        self.id = id
        self.code = code

class ProtocolLeaf:
    def __init__(self, id, code):
        self.id = id
        self.code = code

class ModuleNode(ProtocolLeaf):
    def __init__(self, id, code):
        self.__init__()

    def __init__(self):
        self.id = "module"
        self.code = '0'

class ServoNode(ProtocolNode):
    children = {
        "get_degree" : ProtocolLeaf("get_degree", '1'),
        "set_degree" : ProtocolLeaf("set_degree", '2'),
        "set_degree_steps" : ProtocolLeaf("set_degree_steps", '3')
    }

    def __init__(self, id, code):
        super().__init__(id, code)

class UltraSoundNode(ProtocolNode):
    children = {
        "get_distance" : ProtocolLeaf("get_distance", '1')
    }

    def __init__(self, id, code):
        super().__init__(id, code)

class PIDNode(ProtocolNode):
    children = {
        "toggle_auto" : ProtocolLeaf("toggle_auto", '1'),
        "set_setpoint" : ProtocolLeaf("set_setpoint", '2'),
        "set_tuning" : ProtocolLeaf("set_tuning", '3'),
        "get_tuning" : ProtocolLeaf("get_tuning", '4')
    }

    def __init__(self, id, code):
        super().__init__(id, code)

class NovaNode(ProtocolNode):
    children = {
        "set_mode" : ProtocolLeaf("set_mode", '1'),
        "servo1" : ServoNode("servo1", '1'),
        "servo2" : ServoNode("servo2", '2'),
        "servo3" : ServoNode("servo3", '3'),
        "servo4" : ServoNode("servo4", '4'),
        "servo5" : ServoNode("servo5", '5'),
        "ultrasound" : UltraSoundNode("ultrasound", '6')
    }

    def __init__(self, id, code):
        super().__init__(id, code)

class ExternalInputNode(ProtocolNode):
    children = {
        "servo1" : ServoNode("servo1", '1'),
        "servo2" : ServoNode("servo2", '2'),
        "servo3" : ServoNode("servo3", '3'),
        "servo4" : ServoNode("servo4", '4'),
        "servo5" : ServoNode("servo5", '5')
    }

    def __init__(self, id, code):
        super().__init__(id, code)

class KeepDistanceNode(ProtocolNode):
    children = {
        "set_min_distance" : ProtocolLeaf("set_min_distance", '1'),
        "set_max_distance" : ProtocolLeaf("set_max_distance", '2'),
        "pid" : PIDNode("pid", '1')
    }

    def __init__(self, id, code):
        super().__init__(id, code)

class TrackObjectNode(ProtocolNode):
    children = {
        "set_coordinates" : ProtocolLeaf("set_coordinates", '1'),
        "ack_coordinates" : ProtocolLeaf("ack_coordinates", '2'),
        "pid_x" : PIDNode("pid_x", '1'),
        "pid_y" : PIDNode("pid_y", '2')
    }

    def __init__(self, id, code):
        super().__init__(id, code)

class Root(ProtocolNode):
    children = {
        "nova" : NovaNode("nova", '0'),
        "joystick_absolute" : ProtocolLeaf("joystick_absolute", '1'),
        "joystick_relative" : ProtocolLeaf("joystick_relative", '2'),
        "external_input" : ExternalInputNode("external_input", '3'),
        "keep_distance" : KeepDistanceNode("keep_distance", '4'),
        "track_object" : TrackObjectNode("track_object", '5')
    }

    def __init__(self):
        super().__init__("root", "0")

class NovaProtocolCommandBuilder:

    root = Root()

    def __init__(self):
        self.module = None
        self.asset = None
        self.operation = None
        self.args = []

    def setModule(self, mod_name):
        if mod_name in self.root.children:
            self.module = self.root.children[mod_name]

        return self

    def setAsset(self, asset_name):
        if not self.module == None:
            if asset_name in self.module.children:
                self.asset = self.module.children[asset_name]

        return self

    def setOperation(self, op_name):
        if not self.module == None:
            if op_name in self.module.children:
                self.asset = ModuleNode()
                self.operation = self.module.children[op_name]
            elif self.asset != None and op_name in self.asset.children:
                self.operation = self.asset.children[op_name]

        return self

    def setArgs(self, args_list):
        self.args = args_list

        return self

    def setModeArg(self, module_name):
        self.args.append(self.root.children[module_name].code)

        return self

    def build(self):
        assert self.module != None
        assert self.asset != None
        assert self.operation != None

        return [self.module.code,
            self.asset.code,
            self.operation.code,
            str(len(self.args))] + self.args

def createCommand():
    return NovaProtocolCommandBuilder()

class NovaProtocolCommandReader:
    def __init__(self):
        self.__initLookupTree()

    def __initLookupTree(self):
        self.lookup = {}
        root = Root()
        self.__traverseModules(root)

    def __traverseModules(self, root):
        for k,v in root.children.items():
            if isinstance(v, ProtocolNode):
                self.__traverseAssets(v, [v.code], [v.id])
            else:
                codes = [v.code,'0','0']
                ids = [v.id,'','']
                self.__addToLookup(codes, ids)

    def __traverseAssets(self, node, code_parts, id_parts):
        for k,v in node.children.items():
            if isinstance(v, ProtocolNode):
                codes = code_parts + [v.code]
                ids = id_parts + [v.id]
                self.__traverseOperations(v, codes, ids)
            else:
                codes = code_parts + ['0',v.code]
                ids = id_parts + ['module',v.id]
                self.__addToLookup(codes, ids)

    def __traverseOperations(self, node, code_parts, id_parts):
        for k,v in node.children.items():
            if isinstance(v, ProtocolLeaf):
                codes = code_parts + [v.code]
                ids = id_parts + [v.id]
                self.__addToLookup(codes, ids)

    def __addToLookup(self, code_list, command_list):
        key = ":".join(code_list)
        self.lookup[key] = command_list

    def readCommand(self, cmd_codes):
        cmd = self.lookup[":".join(cmd_codes[:3])]

        if int(cmd_codes[3]) > int(0):
            args = cmd_codes[4:]
        else:
            args = []

        cmd.append(args)

        return cmd

class NovaCommand:
    def __init__(self, type, module, asset, operation, args):
        self.type = type
        self.module = module
        self.asset = asset
        self.operation = operation
        self.args = args

    def toList(self):
        cmd = [self.type, self.module, self.asset, self.operation] + self.args
        return cmd
