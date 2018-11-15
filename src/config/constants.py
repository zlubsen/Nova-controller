class MetaConst(type):
    def __getattr__(cls, key):
        return cls[key]

    def __setattr__(cls, key, value):
        raise TypeError

class Const(object, metaclass=MetaConst):
    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        raise TypeError

class NovaConstants(Const):
    # command template
    CMD_START_MARKER = '>'
    CMD_END_MARKER = '<'
    CMD_SEPARATOR = ':'
    CMD_TEMPLATE = CMD_START_MARKER + "{}:{}:{}:{}:{}" + CMD_END_MARKER
