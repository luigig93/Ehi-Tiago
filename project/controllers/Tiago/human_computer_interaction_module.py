import navigation_module
import json
# import speech_recognition as sr
import search_module
import sys

"""
with open("./credentials_speech_to_text_google.json") as f:
    GOOGLE_CLOUD_SPEECH_CREDENTIALS = json.dumps(json.load(f))
"""


def ask_for_object():
    # questa è l'unica forma di interazione prevista in webots
    object_to_search = sys.argv[1]
    
    # presentazione
    print("Hi, I'm Tiago, and you asked me to search {}".format(sys.argv[1]))
    
    """
    object_to_search = input("Quale oggetto stai cercando?")
  
    #speech to text part
    # obtain audio from the microphone
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Quale oggetto stai cercando?\n")
        audio = r.listen(source)

        # recognize speech using Google Cloud Speech
        try:
            object_to_search = r.recognize_google_cloud(audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS).strip()

        except sr.UnknownValueError:
            print("Google Cloud Speech could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Cloud Speech service; {0}".format(e))
    """
    
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


def ask_for_route_old(graph):
    source = input("source >>")
    target = input("target >>")

    # controllo caso particolare
    if source == target:
        # non fare nulla, l'utente ti ha chiesto ti restare fermo dove sei!
        return ask_for_route(graph)
    elif source[0] == "D" or target[0] == "D":
        # un path non può iniziare o finire in una porta
        # ma può solo iniziare e finire su una pose/landmark
        return ask_for_route(graph)
    elif source[0] == "P" or target[0] == "P":
        return ask_for_route(graph)
    else:
        return navigation_module.calc_route(graph, source, target)


def read_objects_file():
    pass

