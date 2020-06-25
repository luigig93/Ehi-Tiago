import config_tiago
import communication_module
import navigation_module
import basic_module
import human_computer_interaction_module
import search_module
import sys
from controller import Robot


def setup():
    # create robot
    robot = Robot()  

    # init basic system
    basic_module.init_basic_system(robot)

    # init communication system
    communication_module.init_communication_system(robot)

    # init nav system
    map_graph = navigation_module.init_navigation_system(robot)

    return robot, map_graph


def loop(robot, map_graph):
    # init stuff here (only once)
    start_landmark = "L14"
    current_node_id = start_landmark  # La simulazione inizia sempre con Tiago posizionato su un landmark, prevediamo solo navigazioni da landmark a landmark
    path_list, object_to_search = human_computer_interaction_module.ask_for_route(map_graph,current_node_id)
    target_list = path_list[0]
    path_index = 0
    target_index = 0
    navigation_mode = "turn"
    # object_found = False
    
    print("Let's start!")

    # robot loop
    while robot.step(int(robot.getBasicTimeStep())) != -1:
        dist_list = communication_module.receive_msgs(robot)

        if len(dist_list) > 0:
            # calc current position
            current_position = navigation_module.track_pos(dist_list)

            # check stop conditions
            position_tuple = (current_position, target_list[target_index]['position'])
            stop_condition = navigation_module.calc_stop_condition(position_tuple, target_list[target_index]['type'])

            if stop_condition or (current_node_id == target_list[target_index]["name"]):
                # target reached
                basic_module.stop(robot)

                # DEBUG
                print("target {} @{} reached...".format(target_list[target_index]['name'], target_list[target_index]['position']))
                current_node_id = target_list[target_index]["name"]

                # door opening system
                if (target_index > 0) and (target_list[target_index-1]['type'] == 'door'):
                    # se il target precedente era una porta, dobbiamo chiuderla!
                    communication_module.send_request(robot, target_list[target_index-1]['name'], "close")

                # only for landmark
                if target_list[target_index]['type'] == 'landmark' and (current_node_id != start_landmark):
                    navigation_module.look_at_landmark(robot, current_position, target_list[target_index]['viewpoint'])
                    # controlla se l'oggetto da cercare è presente nel landmark
                    object_found = basic_module.look_for_object(target_list[target_index]["name"], object_to_search)
                    # se abbiamo trovato l'oggetto, possiamo terminare la simulazione. 
                    if object_found:
                    	print("Goodbye!")
                    	exit(0)
                    	
                # change target
                target_index += 1
                navigation_mode = "turn"

                if target_index == len(target_list):
                    # change path
                    path_index += 1

                    if (path_index  == len(path_list)):
                        # abbiamo esplorato tutti gli oggetti
                        print("I think {} is not in this home... Goodbye!")
                        exit(0)
                        
                    target_list = path_list[path_index]
                    target_index = 0
                else:
                    # door opening system
                    if target_list[target_index]['type'] == 'door':
                        # il prossimo target è una porta, quindi dobbiamo aprirla!
                        communication_module.send_request(robot, target_list[target_index]['name'], "open")
                        # facciamolo non bloccante, quindi procediamo ad orientarci verso il target
            else:
                prev_navigation_mode = navigation_mode
                navigation_mode = navigation_module.navigate(robot, navigation_mode, position_tuple)
                # door opening system
                if (prev_navigation_mode == "turn") and (target_list[target_index]['type'] == 'door'):
                    if target_list[target_index]['type'] == 'door':
                        # mettiamoci in attesa
                        #prima di procedere bisogna aspettare l'ok del DOS
                        communication_module.receive_notify(robot)
                        # ok, la porta è aperta! procediamo...


if __name__ == "__main__":
    Tiago, home = setup()
    loop(Tiago, home)

