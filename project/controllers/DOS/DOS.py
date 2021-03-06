# door opening system
from controller import Supervisor
import config_dos


def open_door(supervisor, door, side):
    current_position = 0.000
    opened_position = side
    opening_step = config_dos.OPENING_STEP

    if side > 0:
        while round(current_position,3) < opened_position:
            current_position = current_position + opening_step
            set_door_position(door, current_position)
            supervisor.step(config_dos.TIME_STEP)
    else:
        while round(current_position,3) > opened_position:
            current_position = current_position - opening_step
            set_door_position(door, current_position)
            supervisor.step(config_dos.TIME_STEP)

    set_door_position(door, opened_position)


def close_door(supervisor, door, side):
    current_position = round(read_door_position(door),3)
    closed_position = config_dos.CLOSED_POSITION
    closing_step = config_dos.OPENING_STEP

    if side > 0:
        while round(current_position, 3) >= closed_position:
            current_position = current_position - closing_step
            set_door_position(door, current_position)
            supervisor.step(config_dos.TIME_STEP)
    else:
        while round(current_position, 3) <= -closed_position:
            current_position = current_position + closing_step
            set_door_position(door, current_position)
            supervisor.step(config_dos.TIME_STEP)

    # ritoccare chiusura
    set_door_position(door, 0)
    supervisor.step(config_dos.TIME_STEP)


def get_doors_id(supervisor):
    root = supervisor.getRoot()
    children = root.getField("children")
    num_of_children = children.getCount()

    doors_id_list = list()
    for index in range(num_of_children):
        node = children.getMFNode(index)
        name = node.getTypeName()
        id = node.getId()
        if name == "MyDoor":
            doors_id_list.append(id)

    return doors_id_list


def read_door_position(door_node):
    opening_field = door_node.getField('position')
    opening_value = opening_field.getSFFloat()
    return opening_value


def set_door_position(door_node, position):
    opening_field = door_node.getField('position')
    opening_field.setSFFloat(position)


def read_door_name(door_node):
    name_field = door_node.getField('name')
    name_value = name_field.getSFString()
    return name_value


def read_canBeOpen(door_node):
    canBeOpen_field = door_node.getField('canBeOpen')
    canBeOpen_value = canBeOpen_field.getSFBool()
    return canBeOpen_value


def init_doors(supervisor, doors_id):
    doors = dict()
    for id in doors_id:
        door_node = supervisor.getFromId(id)
        name = read_door_name(door_node)
        doors[name] = dict()
        doors[name]["node"] = door_node
        doors[name]["side"] = config_dos.DOOR_OPENING_SIDE[name]

        if read_door_position(door_node) != float(0):
            set_door_position(door_node, float(0))

        doors[name]["status"] = "close"

    return doors


def init_wifi(robot):
    receiver = robot.getReceiver(config_dos.WIFI_RECEIVER)
    receiver.enable(int(robot.getBasicTimeStep()))


def receive_request(robot, doors):
    wifi_receiver = robot.getReceiver(config_dos.WIFI_RECEIVER)

    while robot.step(config_dos.TIME_STEP) != -1:
        # ci sarà sempre un solo messaggio alla volta
        if wifi_receiver.getQueueLength() > 0:
            msg = wifi_receiver.getData().decode()
            wifi_receiver.nextPacket()
            # in msg è contenuto il nome della porta e l'action: aprire o chiudere
            name, mode = msg.split("/")

            if (mode == "open") and (doors[name]["status"] != "open"):
                open_door(robot, doors[name]["node"], doors[name]["side"])
                doors[name]["status"] = "open"

            elif (mode == "close") and (doors[name]["status"] != "close"):
                close_door(robot, doors[name]["node"], doors[name]["side"])
                doors[name]["status"] = "close"

            # se è già aperta resta aperta, se è già chiusa resta chiusa
            return mode


def notify_opening(robot):
    wifi = robot.getEmitter(config_dos.WIFI_EMITTER)
    msg = "OK".encode()
    wifi.send(msg)
    robot.step(config_dos.TIME_STEP)


def setup():
    supervisor = Supervisor()
    doors_id = get_doors_id(supervisor)
    doors = init_doors(supervisor, doors_id)
    init_wifi(supervisor)
    return supervisor, doors


def loop(supervisor_tuple):
    # init stuff here (only once)
    supervisor, doors = supervisor_tuple

    # robot loop
    while supervisor.step(config_dos.TIME_STEP) != -1:
        # resta in ascolto di una richiesta di apertura o chiusura porta da parte del robot
        mode = receive_request(supervisor, doors)
        if mode == "open":
            # notifichiamo solamente l'apertura, perchè il robot è in attesa.
            # notificare la chiusura non serve, il robot è già in una posizione sicura
            notify_opening(supervisor)


if __name__ == "__main__":
    supervisor_tuple = setup()
    loop(supervisor_tuple)


