from controller import Robot
import config
import communication_module
import navigation_module
import basic_module
import human_computer_interaction_module
import search_module


def setup():
    # create robot
    robot = Robot()
    print("Bella, Tiago!")

    # init basic system
    basic_module.init_basic_system(robot)

    # init communication system
    communication_module.init_communication_system(robot)

    # init nav system
    map_graph = navigation_module.init_navigation_system(robot)

    return robot, map_graph


def loop(robot, map_graph):
    # init stuff here (only once)
    # set this only the first time!
    current_node_id = "L6"  # magari chiedilo all'utente! input("dove si trova Tiago?")
    path_list, object_to_search = human_computer_interaction_module.ask_for_route(map_graph,current_node_id)
    target_list = path_list[0]
    path_index = 0
    target_index = 0
    navigation_mode = "turn"
    object_found = False

    # robot loop
    while robot.step(16) != -1:
        dist_list = communication_module.receive_msgs(robot)

        if len(dist_list) > 0:
            # calc current position
            current_position = navigation_module.track_pos(dist_list)
            print("current_position: {}".format(current_position))
            print("target_position: {}".format(target_list[target_index]['position']))

            # check stop conditions
            position_tuple = (current_position, target_list[target_index]['position'])
            stop_condition = navigation_module.calc_stop_condition(position_tuple, target_list[target_index]['type'])
            #stop_condition1 = navigation_module.calc_stop_condition1(position_tuple, config.DIST_ERROR)
            # stop_condition2, target_list[target_index]['reached'] = navigation_module.calc_stop_condition2(
            #    target_list[target_index]['reached'], position_tuple, config.COORDINATE_ERROR)

            if stop_condition or (current_node_id == target_list[target_index]["name"]):
                # target reached
                basic_module.stop(robot)

                # DEBUG
                print("target {} @{} reached...".format(target_list[target_index]['name'], target_list[target_index]['position']))
                current_node_id = target_list[target_index]["name"]

                # trovato il bug!
                # quando il target index == 0, e l'ultimo nodo del path è una porta, abbiamo un problema
                # perchè otteniamo un index uguale a -1, e quindi accediamo all'ultimo nodo
                # se è una porta ci entriamo e richiediamo la chiusura, ma il DOS è in attesa di una richiesta di apertura
                # quindi viene aperta l'ultima porta e si disallinea tutto il protocollo.
                # altro problema: non possiamo fermarci in una porta, imponiamo questa regola
                # altrimenti dobbiamo monitorare lo stato di tutte le porte
                # ma per questioni di sicurezza meglio imporre che una porta si può solo attraversare
                # e il robot non può sostarvi!
                # door opening system
                if (target_index > 0) and (target_list[target_index-1]['type'] == 'door'):
                    # se il target precedente era una porta, dobbiamo chiuderla!
                    # dobbiamo chiudere anche l'eventuale porta aperta e non chiusa in un path precedente
                    # questo gestisce il caso particolare (e che evitermo a prescindere) di un path che termina
                    # in una porta
                    communication_module.send_request(robot, target_list[target_index-1]['name'], "close")

                # only for landmark
                if target_list[target_index]['type'] == 'landmark':
                    navigation_module.look_at_landmark(robot, current_position, target_list[target_index]['viewpoint'])
                    # controlla se l'oggetto da cercare è presente nel landmark
                    object_found = basic_module.look_for_object(target_list[target_index]["name"], object_to_search)


                # change target
                target_index += 1
                navigation_mode = "turn"

                if target_index == len(target_list):
                    # change path
                    path_index += 1

                    if (path_index  == len(path_list)) or object_found:
                        # abbiamo esplorato tutti gli oggetti, oppure abbiamo trovato l'oggetto
                        # chiedere all'utente di cercare un nuovo oggetto
                        path_list, object_to_search = human_computer_interaction_module.ask_for_route(map_graph, current_node_id)
                        path_index = 0
                        object_found = False

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
