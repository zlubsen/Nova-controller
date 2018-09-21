import cv2 as cv
from communication.serial_communication import SerialCommunication
from communication.zmq_status_pub_communication import StatusPubCommunication
from controlloop.window_base import WindowBaseLoop
from controlloop.external_input import ExternalInputControlLoop
from controlloop.keyboard_mouse_input import KeyboardMouseInputLoop
from controlloop.facedetection import FaceDetectionControlLoop
from config.config import NovaConfig

def setupInputLoops():
    global serial_comm
    global keyboard_mouse_input

    serial_comm = SerialCommunication()
    keyboard_mouse_input = KeyboardMouseInputLoop(serial_comm)

    loops = []
    loops.append(serial_comm)
    #loops.append(window_base)
    loops.append(keyboard_mouse_input)
    return loops

def setupControlLoops():
    loops = []
    loops.append(ExternalInputControlLoop(serial_comm))
    loops.append(FaceDetectionControlLoop(serial_comm))
    loops.append(StatusPubCommunication(NovaConfig.COMPCOMM_STATUS_PUB_URI, NovaConfig.STATUS_PUBLISH_FREQUENCY_MS))
    return loops

#def setupWindow():
#    cv.namedWindow(NovaConfig.NOVA_WINDOW_NAME, cv.WINDOW_AUTOSIZE)

def loop():
    cmds = []
    frame = window_base.captureFrame()

    for input_loop in input_loops:
        input_loop.run(frame)
        while input_loop.commandAvailable():
            cmds.append(input_loop.readCommand())

    for control_loop in control_loops:
        control_loop.run(cmds, frame)

    window_base.finaliseFrame(frame)

def main():
    global input_loops
    global control_loops
    global window_base

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
