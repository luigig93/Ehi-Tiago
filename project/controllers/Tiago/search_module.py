# object search module

import os
import json
import config_tiago
import logging
import pandas as pd
import numpy as np
import pymc3 as pm
import networkx as nx

# disable pymc3 log messages
logger = logging.getLogger('pymc3')
logger.setLevel(logging.ERROR)


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
            position = config_tiago.ID_TO_TAG[key]
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
        # print(similar)
        if(len(df.loc[df["object"] == similar]) > max):
            object_most_similar = similar
            max = sum(df.loc[df["object"] == similar].drop("object",1).values[0])

    return object_most_similar


def search_object(table_path, graph, current_position_id, object_to_search):
    assert os.path.exists(table_path)

    df = pd.read_csv(table_path, index_col = 0)
    row = df.loc[df["object"] == object_to_search].drop('object', 1)

    places = row.keys()
    knowledge = row.values[0]
    number_of_places = len(knowledge)

    distances_dict = get_distances(graph, current_position_id)
    distances = [ distances_dict[key] for key in places]

    ####################################################################################################################

    max_distance = max(distances)
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
    print("I think {} could be there:".format(object_to_search))
    
    display_probs(dict(zip(places, pvals)))

    visiting_sequence = sorted(zip(places, pvals),key=lambda x: x[1], reverse=True)
    visiting_sequence = [config_tiago.TAG_TO_ID[tag] for tag,_ in visiting_sequence]
    # tieni solo i migliori 5, e scarta tutti gli zeri
    # valutazione: top1, top3, top5
    return visiting_sequence

