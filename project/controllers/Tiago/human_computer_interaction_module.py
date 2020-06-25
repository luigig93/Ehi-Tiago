import sys
import json
import navigation_module
import search_module


def ask_for_object():
    # questa è l'unica forma di interazione prevista in webots
    object_to_search = sys.argv[1]
    
    # presentazione
    print("Hi, I'm Tiago, and you asked me to search {}".format(sys.argv[1]))
    
    return object_to_search


def ask_for_route(graph, current_node_id):
    object_to_search = ask_for_object()
    landmarks_to_visit = search_module.search_object("table.csv", graph, current_node_id, object_to_search)
    # debug
    print("These are the landmarks I will visit: {}".format(landmarks_to_visit))
    # bisogna calcolare il path per raggiungere ogni landmark
    path_list = list()
    source_id = current_node_id
    for landmark_id in landmarks_to_visit:
        path = navigation_module.calc_route(graph, source=source_id, target=landmark_id)
        path_list.append(path)
        source_id = landmark_id

    return path_list, object_to_search

