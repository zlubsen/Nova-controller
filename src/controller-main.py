import cv2
from communication.serial_communication import SerialCommunication
from controlloop.facedetection import FaceDetectionControlLoop

def setupCommunication():
    return SerialCommunication()

def setupControlLoops():
    loops = []
    loops.append(FaceDetectionControlLoop(comm))
    return loops

def loop():
    comm.run()

    cmds = []
    while comm.commandAvailable():
        cmds.append(comm.readCommand())

    for control_loop in control_loops:
        control_loop.run(cmds)

def main():
    global comm
    global control_loops

    comm = setupCommunication()
    control_loops = setupControlLoops()

    while True:
        loop()

        if (cv2.waitKey(1) & 0xFF) == ord('q'):
            break

def cleanup():
    comm.close()
    for control_loop in control_loops:
        control_loop.cleanup()

if __name__ == '__main__':
    main()
    cleanup()
