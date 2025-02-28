import models.road_network.create_graph as cg
import models.vehicle_models.energy_consumption as ec
import json
import math
import pandas as pd
import random
from pprint import pprint

with open("./data_collection/data/test_data.json", "r") as file:
    complete_road_data = json.load(file)
with open("models/vehicle_models/static_data.json", "r") as file:
    static_data = json.load(file)
with open("models/vehicle_models/vehicle_data.json", "r") as file:
    vehicle_data = json.load(file)
with open("models/vehicle_models/battery_data.json", "r") as file:
    battery_data = json.load(file)


road_network_file = './data_collection/data/random_weight_edge.csv' 
road_df = pd.read_csv(road_network_file)

OCV = battery_data["OCV"]
capacity = battery_data["Capacity"]
R_int = battery_data["R_internal"]
motor_eff = vehicle_data["motor_eff"]

graph = cg.create_osmnx_compatible_graph('./data_collection/data/random_weight_edge.csv')


def simulate_route():
    nodes = road_df["u"].to_list()
    random_values = random.sample(nodes, 2)
    route = cg.dijkstra(graph, random_values[0], random_values[1])

    with open("./data_collection/data/analysed_dis_data.json", "r") as file:
        map_data = json.load(file)


    cg.find_path_with_nodes(map_data, 17585126, 1130492591)

    route_dict = {}

    i = 0
    for i in range(len(route)-1):
        path = cg.find_path_with_nodes(map_data, route[i], route [i + 1])
        route_dict.update(path)


    consumptions = []
    distances = []
    climbs = []

    for path, pathdata in route_dict.items():
        for section, data in pathdata.items():
            if "section" in section: 
                data["velocity"] = 8.9408
                data["acceleration"] = 0
                tract_power = ec.physical_model(vehicle_data, static_data, data)
                batt_power = ec.battery_power_model(tract_power, motor_eff)

                energy = ec.get_edge_consumption(batt_power, data)

                distances.append(data['distance'])
                consumptions.append(energy)
                climbs.append(data['climb'])

    total_distance = sum(distances)
    total_consumption = sum(consumptions)
    total_climb = sum(climbs)

    return total_distance,total_consumption,total_climb