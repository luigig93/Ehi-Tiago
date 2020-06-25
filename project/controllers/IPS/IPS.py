#Indoor Positioning System

import config_ips
from controller import Robot


def gen_beacons():
    return ["B" + str(index) for index in range(config_ips.NUM_OF_BEACONS)]


def set_beacons(robot, beacons):
    emitters_list = list()
    for index in range(config_ips.NUM_OF_BEACONS):
        emitters_list.append(robot.getEmitter(beacons[index]))
        # print("Bella, Antenna#" + str(index) + "!")

    return emitters_list


def send_msgs(emitters_list, msg_list):
    for index in range(config_ips.NUM_OF_BEACONS):
        emitters_list[index].send(msg_list[index])


def setup():
    robot = Robot()
    beacons = gen_beacons()
    emitters_list = set_beacons(robot, beacons)
    return robot, emitters_list


def loop(robot_tuple):
    robot, emitters_list = robot_tuple
    msg_list = [("B" + str(index)).encode() for index in range(config_ips.NUM_OF_BEACONS)]
    send_ratio = config_ips.ADVERT_INTERVAL // int(robot.getBasicTimeStep())
    current_interval = 0

    # robot loop
    while robot.step(int(robot.getBasicTimeStep())) != -1:
        if current_interval == 0:
            send_msgs(emitters_list, msg_list)
            current_interval = send_ratio
        else:
            current_interval -= 1


if __name__ == "__main__":
    robot_tuple = setup()
    loop(robot_tuple)

