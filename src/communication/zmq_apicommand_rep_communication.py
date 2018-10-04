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

    # TODO add nova config item for polling interval
    # TODO revisit send/receive flags and poller to make more robust (cmds must be ack'd)
    def __listenForCommand(self):
        incoming_cmd = None
        socks = dict(self.poller.poll(200))
        if socks.get(self.server) == zmq.POLLIN:
            try:
                incoming_cmd = self.server.recv_pyobj()
                self.server.send_pyobj(("Ack"), flags=zmq.NOBLOCK)
            except zmq.error.ZMQError:
                print("ZMQError occurred while receiving a command from Nova-REST.")

        return incoming_cmd

    def commandAvailable(self):
        return len(self.receivedCommands) > 0

    def readCommand(self):
        return self.receivedCommands.popleft()

    def run(self):
        api_cmd = self.__listenForCommand()

        if not api_cmd == None:
            print(f"received api-command: {api_cmd}")
            self.receivedCommands.append(api_cmd)

    def cleanup(self):
        self.server.close()
        self.context.term()
        self.poller.unregister()
