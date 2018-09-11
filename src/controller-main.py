import cv2 as cv
from communication.serial_communication import SerialCommunication
from communication.zmq_status_pub_communication import StatusPubCommunication
from controlloop.keyboard_mouse_input import KeyboardMouseInputLoop
from controlloop.keyboard_mouse_output import KeyboardMouseControlLoop
from controlloop.facedetection import FaceDetectionControlLoop
from config.config import NovaConfig

def setupInputLoops():
    global serial_comm
    global keyboard_mouse_input

    serial_comm = SerialCommunication()
    keyboard_mouse_input = KeyboardMouseInputLoop(serial_comm)

    loops = []
    loops.append(serial_comm)
    loops.append(keyboard_mouse_input)
    return loops

def setupControlLoops():
    loops = []
    loops.append(KeyboardMouseControlLoop(serial_comm))
    #loops.append(FaceDetectionControlLoop(serial_comm))
    loops.append(StatusPubCommunication(NovaConfig.COMPCOMM_STATUS_PUB_URI, NovaConfig.STATUS_PUBLISH_FREQUENCY_MS))
    return loops

def setupWindow():
    cv.namedWindow(NovaConfig.NOVA_WINDOW_NAME, cv.WINDOW_AUTOSIZE)

def loop():
    cmds = []

    for input_loop in input_loops:
        input_loop.run()
        while input_loop.commandAvailable():
            cmds.append(input_loop.readCommand())

    for control_loop in control_loops:
        control_loop.run(cmds)

def main():
    global input_loops
    global control_loops

    setupWindow()
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
    cv.destroyAllWindows()

if __name__ == '__main__':
    main()
    cleanup()
