import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import models.road_network.create_graph as cg 
import simulation.simulate_routes as sr 
import models.vehicle_models.battery_deg as bd 
from pprint import pprint


def import_data()->tuple:
    '''
    Import key files, returns:
    road_network_file: path of edge data csv
    road_df: edge data csv
    static_data: dictionary of static parameters
    vehicle_data: dictionary of vehicle parameters
    battery_data: dictionary of battert parameters
    map_data: dictionary of route data
    weights: dictionary of optimal weight parameters

    '''
    with open("models/vehicle_models/static_data.json", "r") as file:
        static_data = json.load(file)
    with open("models/vehicle_models/vehicle_data.json", "r") as file:
        vehicle_data = json.load(file)
    with open("models/vehicle_models/battery_data.json", "r") as file:
        battery_data = json.load(file)
    with open("./data_collection/data/large_net/fixed_large_dis_data.json", "r") as file:
        map_data = json.load(file)
    
    with open("./data_collection/weights.json", "r") as file:
        weights = json.load(file)

    road_network_file = './data_collection/data/large_net/large_edge_data.csv' 
    road_df = pd.read_csv(road_network_file)

    print("data imported")
    return road_network_file, road_df, static_data, vehicle_data, battery_data, map_data, weights

def create_random_test_set(length:int, road_df):
    import random
    u_list = road_df['u'].to_list()
    v_list = road_df['v'].to_list()
    # Combine both lists to get all available nodes
    all_nodes = u_list + v_list
    
    # Remove duplicates by converting to set and back to list
    unique_nodes = list(set(all_nodes))
    
    # Make sure we have enough nodes for the requested pairs
    if len(unique_nodes) < 2:
        raise ValueError("Not enough unique nodes to create pairs")
    
    # Create test set of random pairs
    test_set = []
    while len(test_set) < length:
        # Sample 2 nodes without replacement to ensure they're different
        node_pair = random.sample(unique_nodes, 2)
        
        # Create the tuple and add to test set
        pair = [node_pair[0], node_pair[1]]
        
        # Optionally, check if this exact pair already exists in the test set
        # Uncomment if you want to ensure unique pairs
        if pair not in test_set and [pair[1], pair[0]] not in test_set:
            test_set.append(pair)
        
        # If you're close to exhausting all possible pairs, you might want to break
        # This is just a precaution and likely won't be needed with large graphs
        if len(test_set) == (len(unique_nodes) * (len(unique_nodes) - 1)) // 2:
            break

    return test_set

def create_new_test_set(road_df):
    test_set_dict = {}
    for i in range(1,6):
        test_set = create_random_test_set(500, road_df)
        test_set_dict[f'test_set{i}'] = test_set
    with open("test_data/test_route_set.json", "w") as file:
        json.dump(test_set_dict, file, indent=4)
    