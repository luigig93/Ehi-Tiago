# navigation module

from networkx.readwrite.graphml import read_graphml
from networkx.algorithms.shortest_paths.generic import shortest_path
import math
import random
import basic_module
import config
import communication_module


def init_navigation_system(robot):
    init_inertial(robot)
    map_graph = init_map()
    return map_graph


def init_inertial(robot):
    inertial = robot.getInertialUnit(config.INERTIAL_UNIT)
    inertial.enable(int(robot.getBasicTimeStep()))


def read_inertial(robot):
    inertial = robot.getInertialUnit(config.INERTIAL_UNIT)
    yaw = int(math.degrees(inertial.getRollPitchYaw()[2]))
    if yaw < 0:
        yaw = yaw + 360

    # necessario per mantenere convenzione est a destra e ovest a sinistra
    yaw = 360 - yaw

    # sempre per convenzione
    if yaw == 360:
        yaw = 0

    return yaw


# pare funzionare decentemente!
# non importa l'ordine, basta essere coerenti con i valori di posizione e distanza
# attenzione alle coordinate e al sistema di riferimetno!
# posizionare il robot in posizione (0,0) e a partire da quella posizione posizionare tutti i bGM facendo riferimento
# a quella posizione
def track_pos(dist_list):
    def get_key(item):
        return item[1]

    # prendiamo i 3 beacon più vicini
    sorted_beacon = sorted(dist_list, key=get_key)
    nearest_beacon = sorted_beacon[:3]

    # dist list = [...,("B#", dist),...]
    x1, y1 = config.BEACONS_POS_DICT[nearest_beacon[0][0]]
    x2, y2 = config.BEACONS_POS_DICT[nearest_beacon[1][0]]
    x3, y3 = config.BEACONS_POS_DICT[nearest_beacon[2][0]]

    r1 = nearest_beacon[0][1]
    r2 = nearest_beacon[1][1]
    r3 = nearest_beacon[2][1]

    A = 2*x2 - 2*x1
    B = 2*y2 - 2*y1
    C = r1**2 - r2**2 - x1**2 + x2**2 - y1**2 + y2**2
    D = 2*x3 - 2*x2
    E = 2*y3 - 2*y2
    F = r2**2 - r3**2 - x2**2 + x3**2 - y2**2 + y3**2

    try:
        x = (C*E - F*B) / (E*A - B*D)
        y = (C*D - A*F) / (B*D - A*E)

    except ZeroDivisionError:
        # bisogna cambiare beacon, perchè abbiamo trovato tre beacon allineati verticalmente o orizzontalmente!
        # sostituiamo un beacon casuale con quello leggermente più lontano
        sub_index = random.randint(0,2)
        nearest_beacon[sub_index] = sorted_beacon[3]
        # andiamo in ricorsione, tanto prima o poi trovo quello giusto
        y, x = track_pos(nearest_beacon)

    return round(y,1), round(x,1)


def calc_heading(from_point, to_point):
    X = 0
    Y = 1

    # caso particolare: retta verticale (stesso valore delle x)
    if from_point[X] == to_point[X]:
        # ho una retta verticale, quindi so già cosa fare
        angle = 90
    else:
        coeff_angolare = (from_point[Y] - to_point[Y]) / (from_point[X] - to_point[X])
        angle = int(abs(math.degrees(math.atan(coeff_angolare))))

    # ora bisogna trovare l'angolo corretto in base alle posizioni reciproche delle coordinate
    if from_point[X] <= to_point[X] and from_point[Y] <= to_point[Y]:
        # primo quadrante
        angle = 90 - angle
    elif from_point[X] > to_point[X] and from_point[Y] <= to_point[Y]:
        # secondo quadrante
        angle = 270 + angle
    elif from_point[X] > to_point[X] and from_point[Y] > to_point[Y]:
        # terzo quadrante
        angle = 270 - angle
    if from_point[X] <= to_point[X] and from_point[Y] > to_point[Y]:
        # quarto quadrante
        angle = 90 + angle

    return angle


def calc_route(graph, source, target):
    target_list = list()
    # scartiamo il primo nodo, perchè ci troviamo già su quello (sistema di posizionamento non troppo preciso)
    path = shortest_path(graph,source,target,weight='distance') #[1:]

    for node in path:
        target = dict()
        target['name'] = node
        target['position'] = graph.nodes[node]['z'], graph.nodes[node]['x'] # formato punti target (z, x)
        target['room'] = graph.nodes[node]['room_id']
        target['type'] = graph.nodes[node]['type']
        target['reached'] = [False, False]

        if target['type'] == 'landmark':
            target['viewpoint'] = graph.nodes[node]['orientation_z'], graph.nodes[node]['orientation_x']
            target['object'] = graph.nodes[node]['rec_name']

        target_list.append(target)

    return target_list


def init_map():
    graph = read_graphml(path='map.graphml')
    return graph


def calc_distance(c_pos, t_pos):
    z = (c_pos[0] - t_pos[0])**2
    x = (c_pos[1] - t_pos[1])**2
    return round(math.sqrt(z + x),2)


def init_gps(robot):
    # get gps sensor
    gps_sensor = robot.getGPS(config.GPS_SENSOR)
    gps_sensor.enable(int(robot.getBasicTimeStep()))


def read_gps(robot):
    gps_sensor = robot.getGPS(config.GPS_SENSOR)
    gps_pos = gps_sensor.getValues()
    return round(gps_pos[2],2), round(gps_pos[0],2)


def calc_stop_condition(position_tuple, target_type):
    error = config.NAV_ERROR

    current_position, target_position = position_tuple
    condition_z = (target_position[0] - error) <= current_position[0] <= (target_position[0] + error)
    condition_x = (target_position[1] - error) <= current_position[1] <= (target_position[1] + error)
    condition = condition_z and condition_x
    return condition


def calc_stop_condition1(position_tuple, distance_error):
     current_position, target_position = position_tuple
     current_distance = calc_distance(current_position, target_position)
     print("current distance: {}".format(current_distance))
     condition = current_distance <= distance_error
     return condition


def calc_stop_condition2(target_reached, position_tuple, coordinate_error):
    current_pos_z, current_pos_x = position_tuple[0]
    target_pos_z, target_pos_x = position_tuple[1]
    target_z_reached, target_x_reached = target_reached

    if not target_z_reached:
        #print("target z not reached...")
        if (target_pos_z - coordinate_error) <= current_pos_z <= (target_pos_z + coordinate_error):
            #print("target z reached")
            target_z_reached = True

    if not target_x_reached:
       # print("target x not reached...")
        if (target_pos_x - coordinate_error) <= current_pos_x <= (target_pos_x + coordinate_error):
         #   print("target x reached...")
            target_x_reached = True

    condition = target_z_reached and target_x_reached

    return  condition, (target_z_reached, target_x_reached)


def navigate(robot, navigation_mode, position_tuple):
    current_position, target_position = position_tuple

    if navigation_mode == "forward":
        print("forward...")
        # check distance from target
        # braking system
        distance_to_target = calc_distance(current_position, target_position)
        basic_module.linear_braking_system(robot, distance_to_target)

    elif navigation_mode == "turn":
        print("turn...")
        # turn (this is a complete turn)
        basic_module.turn(robot, start_position=current_position, target_position=target_position)
        navigation_mode = "adjust"

    elif navigation_mode == "adjust":
        print("adjust...")
        # bisogna intervenire qui
        basic_module.turn(robot, start_position=current_position, target_position=target_position)
        navigation_mode = "forward"
        basic_module.go_forward(robot, config.CRUISE_SPEED)

    return navigation_mode


def look_at_landmark(robot, current_position, landmark_viewpoint):
    basic_module.turn(robot, start_position=current_position, target_position=landmark_viewpoint)
