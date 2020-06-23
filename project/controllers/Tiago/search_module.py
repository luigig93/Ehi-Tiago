# object search module

import pandas as pd
import numpy as np
import os
import pymc3 as pm
import networkx as nx
import json
import speech_recognition as sr
import gensim
import config


with open("./credentials_speech_to_text_google.json") as f:
    GOOGLE_CLOUD_SPEECH_CREDENTIALS = json.dumps(json.load(f))


def display_probs(d):
    for key, value in d.items():
        print(f'Place: {key:8} Prevalence: {100*value:.2f}%.')


def init_search_module():
    gmodel = gensim.models.KeyedVectors.load_word2vec_format("model.vec")
    return gmodel


def get_distances(graph, source_id):

    distances = nx.shortest_path_length(graph, source=source_id, weight="distance" )

    distances_filtered = dict()

    for key in distances.keys():
        if key[0] == "L":
            position = config.ID_TO_TAG[key]
            distances_filtered[position] = distances[key]

    return distances_filtered


def check_similar_objects(df, gmodel, object_to_search):

    max = 0
    object_most_similar = None

    try:
        similars = gmodel.most_similar(positive=[object_to_search], topn=10)
    except KeyError: #object not present in the table
        return None

    similars = [x for x,_ in similars]

    for similar in similars:
        print(similar)
        if(len(df.loc[df["object"] == similar]) > max):
            object_most_similar = similar
            max = sum(df.loc[df["object"] == similar].drop("object",1).values[0])

    return object_most_similar


def search_object(table_path, graph, current_position_id, object_to_search):
    assert os.path.exists(table_path)

    df = pd.read_csv(table_path, index_col = 0)
    row = df.loc[df["object"] == object_to_search].drop('object', 1)

    for x in list(zip(row.keys() ,row.values[0])):
        print(str(x[0]) + " " + str(x[1]))

    places = row.keys()
    knowledge = row.values[0]
    number_of_places = len(knowledge)

    # node_id = ("pose",7.3533,2.2700,"corridor-2")
    distances_dict = get_distances(graph, current_position_id)
    distances = [ distances_dict[key] for key in places]

    ####################################################################################################################

    max_distance = max(distances)

    print("Sommatoria = " + str(sum(distances)) + " numero osservazioni = " + str(sum(knowledge)) + "Rapporto S/o =" + str(sum(distances)/sum(knowledge)))

    # inverted_distances = list(map(lambda x: abs(x-max_distance+1)/3, distances))
    inverted_distances = list(map(lambda x: abs(x-max_distance+3)/3, distances))

    prior_knowledge = np.array(inverted_distances)

    with pm.Model() as model:
        # Parameters of the Multinomial are from a Dirichlet
        parameters = pm.Dirichlet('parameters', a=prior_knowledge, shape=number_of_places)
        # Observed data is from a Multinomial distribution
        observed_data = pm.Multinomial(
            'observed_data', n=sum(knowledge), p=parameters, shape=number_of_places, observed=knowledge)

    with model:
        # Sample from the posterior
        trace = pm.sample(draws=1000, chains=2, tune=500,
                          discard_tuned_samples=True)

        trace_df = pd.DataFrame(trace['parameters'], columns = places)

    # For probabilities use samples after burn in
    pvals = trace_df.iloc[:, :number_of_places].mean(axis = 0)

    ###################################################################################################################
    display_probs(dict(zip(places, pvals)))

    #(bedroom-bed, xxx)
    visiting_sequence = sorted(zip(places, pvals),key=lambda x: x[1], reverse=True)
    visiting_sequence = [config.TAG_TO_ID[tag] for tag,_ in visiting_sequence]
    # tieni solo i migliori 5, e scarta tutti gli zeri
    # valutazione: top1, top3, top5
    return visiting_sequence





