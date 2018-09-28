import zmq
from collections import deque

class APICommandRepCommunication:
    def __init__(self, uri="tcp://*:5556"):
        self.__setupZMQ(uri)
        self.receivedCommands = deque()

    def __setupZMQ(self, uri):
        self.context = zmq.Context()
        self.server = self.context.socket(zmq.REP)
        self.server.bind(uri)

        self.poller = zmq.Poller()
        self.poller.register(self.server, zmq.POLLIN)

    def __listenForCommand(self):
        api_cmd = None
        socks = dict(self.poller.poll(500))
        if socks.get(self.server) == zmq.POLLIN:
            api_cmd = self.server.recv_pyobj()

        return api_cmd

    def readCommand(self):
        return self.receivedCommands.popleft()

    def run(self, cmds):
        api_cmd = self.__listenForCommand()

        if not api_cmd == None:
            self.receivedCommands.append(api_cmd)

    def cleanup(self):
        pass
