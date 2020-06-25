# communication module 

import math
import config_tiago
import basic_module


def init_communication_system(robot):
    init_receiver(robot)


def init_receiver(robot):
    # bluetooth
    bluetooth_receiver = robot.getReceiver(config_tiago.BLUETOOTH_RECEIVER)
    bluetooth_receiver.enable(int(robot.getBasicTimeStep()))

    # wifi
    wifi_receiver = robot.getReceiver(config_tiago.WIFI_RECEIVER)
    wifi_receiver.enable(int(robot.getBasicTimeStep()))


def clean_msg_queue(robot):
    bluetooth_receiver = robot.getReceiver(config_tiago.BLUETOOTH_RECEIVER)
    while (bluetooth_receiver.getQueueLength() > config_tiago.NUM_OF_BEACONS):
        bluetooth_receiver.nextPacket()  # scarta il messaggio


def receive_msgs(robot):
    dist_list = list()
    recv = robot.getReceiver(config_tiago.BLUETOOTH_RECEIVER)
    # devo prendere gli ultimi NUM_OF_BEACONS elementi della coda!
    # serve un ciclo di svuotamento dei messaggi meno recenti
    clean_msg_queue(robot)

    while recv.getQueueLength() >= 1:
        msg = recv.getData().decode()
        distance = 1 / math.sqrt(recv.getSignalStrength())
        dist_list.append((msg, distance))
        recv.nextPacket()

    return dist_list


def send_request(robot, door, mode):
    wifi = robot.getEmitter(config_tiago.WIFI_EMITTER)
    msg = "{}/{}".format(door,mode).encode()
    wifi.send(msg)
    basic_module.step(robot)


def receive_notify(robot):
    wifi_receiver = robot.getReceiver(config_tiago.WIFI_RECEIVER)

    while robot.step(int(robot.getBasicTimeStep())) != -1:
        # ci sarà sempre un solo messaggio alla volta
        if wifi_receiver.getQueueLength() == 1:
            msg = wifi_receiver.getData().decode()
            wifi_receiver.nextPacket()
            if msg == "OK":
                return

