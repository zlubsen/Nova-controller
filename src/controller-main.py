import cv2 as cv
from communication.serial_communication import SerialCommunication
from communication.zmq_status_pub_communication import StatusPubCommunication
from communication.zmq_apicommand_rep_communication import APICommandRepCommunication
from controlloop.window_base import WindowBaseLoop
from controlloop.external_input import ExternalInputControlLoop
from controlloop.keyboard_mouse_input import KeyboardMouseInputLoop
from controlloop.facedetection import FaceDetectionControlLoop
from config.config import NovaConfig

def setupInputLoops():
    global serial_comm
    global keyboard_mouse_input

    serial_comm = SerialCommunication()
    keyboard_mouse_input = KeyboardMouseInputLoop(serial_comm, status_dict)
    api_comm = APICommandRepCommunication(uri=NovaConfig.COMPCOMM_COMMAND_URI)

    loops = []
    loops.append(serial_comm)
    loops.append(keyboard_mouse_input)
    loops.append(api_comm)
    return loops

def setupControlLoops():
    loops = []
    loops.append(ExternalInputControlLoop(serial_comm, status_dict))
    loops.append(FaceDetectionControlLoop(serial_comm, status_dict))
    #loops.append(StatusPubCommunication(status_dict, NovaConfig.COMPCOMM_STATUS_PUB_URI, NovaConfig.STATUS_PUBLISH_FREQUENCY_MS))
    return loops

def setupStatusDict():
    statusdict = {}
    statusdict["current_mode"] = NovaConfig.STARTUP_MODE

    return statusdict

def loop():
    global status_dict

    cmds = []
    status_dict["frame"] = window_base.captureFrame()

    for input_loop in input_loops:
        input_loop.run()
        while input_loop.commandAvailable():
            cmds.append(input_loop.readCommand())

    for control_loop in control_loops:
        control_loop.run(cmds)

    window_base.finaliseFrame(status_dict["frame"])
    status_dict.pop("frame", None)

def main():
    global input_loops
    global control_loops
    global window_base
    global status_dict

    status_dict = setupStatusDict()

    window_base = WindowBaseLoop()
    input_loops = setupInputLoops()
    control_loops = setupControlLoops()

    while keepRunning():
        loop()

def keepRunning():
    return keyboard_mouse_input.isRunning() # add different kill signal sources if needed

def cleanup():
    for control_loop in control_loops:
        control_loop.cleanup()

    serial_comm.close()

if __name__ == '__main__':
    main()
    cleanup()
