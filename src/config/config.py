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

class NovaConfig(Const):
    SERIAL_BAUDRATE = 28800
    SERIAL_PORT_WINDOWS = 'COM4'
    SERIAL_PORT_MACOS = '' # TODO set correct port for macos
    SERIAL_PORT_LINUX = '' # TODO set correct port for Linux

    COMPCOMM_STATUS_PUBSUB_SOCKET = 8888
    COMPCOMM_STATUS_PUB_URI = f"tcp://*:{COMPCOMM_STATUS_PUBSUB_SOCKET}"
    COMPCOMM_STATUS_SUB_URI = f"tcp://localhost:{COMPCOMM_STATUS_PUBSUB_SOCKET}"
    COMPCOMM_COMMAND_SOCKET = 8889
    COMPCOMM_COMMAND_URI = f"tcp://*:{COMPCOMM_COMMAND_SOCKET}"

    STATUS_PUBLISH_FREQUENCY_MS = 2000
