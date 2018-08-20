import cv2
from communication.serial_communication import SerialCommunication
from communication.zmq_status_pub_communication import StatusPubCommunication
from controlloop.facedetection import FaceDetectionControlLoop
from config.config import NovaConfig

def setupSerialCommunication():
    return SerialCommunication()

def setupCompCommunication():
    return StatusPubCommunication(NovaConfig.COMPCOMM_STATUS_PUB_URI, NovaConfig.STATUS_PUBLISH_FREQUENCY_MS)

def setupControlLoops():
    loops = []
    loops.append(FaceDetectionControlLoop(serial_comm))
    return loops

def loop():
    serial_comm.run()

    cmds = []
    while serial_comm.commandAvailable():
        cmds.append(serial_comm.readCommand())

    for control_loop in control_loops:
        control_loop.run(cmds)
        zmq_publish_comm.run(cmds)

def main():
    global serial_comm
    global zmq_publish_comm
    global control_loops

    serial_comm = setupSerialCommunication()
    zmq_publish_comm = setupCompCommunication()
    control_loops = setupControlLoops()

    while True:
        loop()

        if (cv2.waitKey(1) & 0xFF) == ord('q'):
            break

def cleanup():
    serial_comm.close()
    for control_loop in control_loops:
        control_loop.cleanup()

if __name__ == '__main__':
    main()
    cleanup()
