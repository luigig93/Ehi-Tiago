# basic system module

import config_tiago
import navigation_module
import communication_module


def init_basic_system(robot):
    init_motors(robot)


def step(robot):
    if robot.step(int(robot.getBasicTimeStep())) == -1:
        exit(config_tiago.EXIT_SUCCESS)


def init_motors(robot):
    # get motors devices
    left_wheel = robot.getMotor(config_tiago.LEFT_WHEEL_MOTOR)
    right_wheel = robot.getMotor(config_tiago.RIGHT_WHEEL_MOTOR)

    # init motors
    left_wheel.setPosition(config_tiago.INFINITY)
    right_wheel.setPosition(config_tiago.INFINITY)
    left_wheel.setVelocity(config_tiago.NULL_SPEED)
    right_wheel.setVelocity(config_tiago.NULL_SPEED)

    # get and enable sensors devices
    # wheel positions sensors
    left_pos_sensor = robot.getPositionSensor(config_tiago.LEFT_WHEEL_SENSOR)
    right_pos_sensor = robot.getPositionSensor(config_tiago.RIGHT_WHEEL_SENSOR)
    left_pos_sensor.enable(int(robot.getBasicTimeStep()))
    right_pos_sensor.enable(int(robot.getBasicTimeStep()))

    # force and torque sensors
    # wheel forces
    left_wheel.enableForceFeedback(int(robot.getBasicTimeStep()))
    left_wheel.enableForceFeedback(int(robot.getBasicTimeStep()))
    right_wheel.enableTorqueFeedback(int(robot.getBasicTimeStep()))
    right_wheel.enableTorqueFeedback(int(robot.getBasicTimeStep()))


def go_forward(robot, speed):
    # get motors devices
    left_wheel = robot.getMotor(config_tiago.LEFT_WHEEL_MOTOR)
    right_wheel = robot.getMotor(config_tiago.RIGHT_WHEEL_MOTOR)

    left_wheel.setVelocity(speed)
    right_wheel.setVelocity(speed)


def stop(robot, num_of_iter=100):
    # get motors devices
    left_wheel = robot.getMotor(config_tiago.LEFT_WHEEL_MOTOR)
    right_wheel = robot.getMotor(config_tiago.RIGHT_WHEEL_MOTOR)

    left_wheel.setVelocity(config_tiago.NULL_SPEED)
    right_wheel.setVelocity(config_tiago.NULL_SPEED)

    # this is a complete cycle of stop
    for i in range(num_of_iter):
        step(robot)


def calc_turning_direction(start_head, target_head):
    # pre processing
    right_half = [head % 360 for head in range(start_head, start_head + 180)]

    # calc direction
    if target_head in right_half:
        # senso orario
        direction = config_tiago.CLOCK_WISE
    else:
        # senso antiorario
        direction = config_tiago.COUNTER_CLOCK_WISE

    return direction


def set_motor_turn(robot, direction, speed=config_tiago.TURNING_SPEED):
    # get motors devices
    left_wheel = robot.getMotor(config_tiago.LEFT_WHEEL_MOTOR)
    right_wheel = robot.getMotor(config_tiago.RIGHT_WHEEL_MOTOR)

    # set turning speed
    left_wheel.setVelocity(direction * speed)
    right_wheel.setVelocity(-direction * speed)


def check_heading_bug(heading):
    return 179 if heading == 180 else heading



def turn(robot, start_position, target_position):

    target_head = navigation_module.calc_heading(start_position, target_position)

    # c'è un bug nell'inerziale, il 180 non viene rilevato
    target_head = check_heading_bug(target_head)
    # print("target heading: {}".format(target_head))

    # read start heading
    start_head = navigation_module.read_inertial(robot)

    # calc turning direction
    direction = calc_turning_direction(start_head, target_head)

    # set motor for turning
    set_motor_turn(robot,direction)

    # turn
    while navigation_module.read_inertial(robot) != target_head:
        rotational_braking_system(robot, target_head, direction)
        step(robot)
        # ho aggiornato la simulazione, quindi qua sono già disponibili i nuovi messaggi

    stop(robot)


def rotational_braking_system(robot, target_head, direction):
    t_head = 360 if target_head == 0 else target_head
    offset = abs(navigation_module.read_inertial(robot) - t_head)

    if offset <= 15:
        speed = 0.5
        set_motor_turn(robot, direction, speed)
    elif offset <= 5:
        speed = 0.2
        set_motor_turn(robot, direction, speed)


def linear_braking_system(robot, distance_to_target):
    if distance_to_target <= 0.5:
        go_forward(robot, 1)
    elif distance_to_target <= 0.3:
        go_forward(robot, 0.5)


def move_head(robot):
    # get motor device
    head_rl = robot.getMotor(config_tiago.HEAD_RL)
    # get motor sensor
    head_rl_sensor = robot.getPositionSensor(config_tiago.HEAD_RL_SENSOR)

    # set position
    head_rl.setPosition(head_rl.getMaxPosition())
    head_rl.setVelocity(0.3)

    MY_MAX = 1.2
    MY_MIN = -1.2

    to_max = True
    to_min = False

    while True:
        if(to_max and (head_rl_sensor.getValue() >= MY_MAX)):
            # inverti
            # print("inverti!")
            to_max = False
            to_min = True
            head_rl.setPosition(head_rl.getMinPosition())

        if(to_min and (head_rl_sensor.getValue() <= MY_MIN)):
            # inverti
            # print("inverti!")
            to_min = False
            to_max = True
            head_rl.setPosition(head_rl.getMaxPosition())

        step(robot)


def init_motor_sensors(robot):
    # get sensors devices
    # wheel
    left_pos_sensor = robot.getPositionSensor(config_tiago.LEFT_WHEEL_SENSOR)
    right_pos_sensor = robot.getPositionSensor(config_tiago.RIGHT_WHEEL_SENSOR)
    #head
    head_rl_sensor = robot.getPositionSensor(config_tiago.HEAD_RL_SENSOR)
    head_ud_sensor = robot.getPositionSensor(config_tiago.HEAD_UD_SENSOR)
    # torso
    torso_lift_sensor  = robot.getPositionSensor(config_tiago.TORSO_LIFT_SENSOR)

    left_pos_sensor.enable(int(robot.getBasicTimeStep()))
    right_pos_sensor.enable(int(robot.getBasicTimeStep()))
    head_rl_sensor.enable(int(robot.getBasicTimeStep()))
    head_ud_sensor.enable(int(robot.getBasicTimeStep()))
    torso_lift_sensor.enable(int(robot.getBasicTimeStep()))


def go_backward(robot, speed):
    # get motors devices
    left_wheel = robot.getMotor(config_tiago.LEFT_WHEEL_MOTOR)
    right_wheel = robot.getMotor(config_tiago.RIGHT_WHEEL_MOTOR)

    left_wheel.setVelocity(-speed)
    right_wheel.setVelocity(-speed)


def passive_wait(robot, seconds):
    start_time = robot.getTime()
    while True:
        # at least once
        step(robot)
        if start_time + seconds > robot.getTime(): break


def look_for_object(landmark_id, object_to_search):
    print("searching {} @{}".format(object_to_search,landmark_id))
    
    if object_to_search in config_tiago.HOME_OBJECTS[landmark_id]:
        # oggetto trovato!
        print("{} found @{}".format(object_to_search, landmark_id))
        return True
    else:
        # oggetto non trovato
        print("{} not found @{}".format(object_to_search, landmark_id))
        return False
