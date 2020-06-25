# object search module

import os
import json
import config_tiago
import logging
import itertools
import six
import sys
sys.modules['sklearn.externals.six'] = six
import mlrose
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


def get_distances(graph, source_id):

    distances = nx.shortest_path_length(graph, source=source_id, weight="distance" )

    distances_filtered = dict()

    for key in distances.keys():
        if key[0] == "L":
            position = config_tiago.ID_TO_TAG[key]
            distances_filtered[position] = distances[key]

    return distances_filtered


def rotate(l, n):
    return l[n:] + l[:n]


def search_object(table_path, graph, current_position_id, object_to_search, visited_places):		
    assert os.path.exists(table_path)

    df = pd.read_csv(table_path, index_col = 0)
    
    ####################################################################################################################
    #row = df.loc[df["object"] == object_to_search].drop('object', 1)
    #places = row.keys()
    
    
    df = df.loc[df["object"] == object_to_search].drop('object', 1)
    places = list(df.keys())

    #dropping places already visited
    for visited_place in visited_places:
        try:
            visited_place = config_tiago.ID_TO_TAG[visited_place]  # translate
            df = df.drop(visited_place, 1)
            places.remove(visited_place)
        except:
            print(visited_place + " not found\n")
	
    # abbiamo visitato tutti i posti, quindi bisogna terminare la simulazione, oggetto non presente in casa!
    if(len(places) == 0):
        return []

    row = df
    
    ####################################################################################################################
    
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
    
    tag_and_dist = sorted(zip(places, pvals), key = lambda x: x[1], reverse=True)
    display_probs(dict(tag_and_dist))
    
    top_4_places = list() # [x[0] for x in tag_and_dist[:5]]
    
    counter = float(0)
    for place, prob in tag_and_dist:
        counter += prob
        top_4_places.append(place)
        if counter >= 0.60:
                break
    
    top_4_places_id = [config_tiago.TAG_TO_ID[tag] for tag in top_4_places]    
    top_5_nodes_id = list(set(top_4_places_id + [current_position_id]))
    
    subgraph = nx.Graph()
    edges = list(itertools.combinations(graph.subgraph(top_5_nodes_id),2))
    all_distances = dict(nx.all_pairs_shortest_path_length(graph))
    edges_with_weight = [ (top_5_nodes_id.index(x[0]), top_5_nodes_id.index(x[1]),all_distances[x[0]][x[1]]) for x in edges]
   
    fitness_dists = mlrose.TravellingSales(distances = edges_with_weight)
    problem_fit = mlrose.TSPOpt(length = len(top_5_nodes_id), fitness_fn = fitness_dists, maximize=False)
    best_state, best_fitness = mlrose.genetic_alg(problem_fit, random_state = 2)
    
    path = [top_5_nodes_id[x] for x in best_state]
    
    visiting_sequence = rotate(path, path.index(current_position_id))

    # visiting_sequence = sorted(zip(places, pvals),key=lambda x: x[1], reverse=True)
    #visiting_sequence = [config_tiago.TAG_TO_ID[tag] for tag,_ in visiting_sequence]
    # tieni solo i migliori 5, e scarta tutti gli zeri
    # valutazione: top1, top3, top5
    visiting_sequence = visiting_sequence[1:]
    
    return visiting_sequence

