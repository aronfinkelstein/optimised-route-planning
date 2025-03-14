import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import models.road_network.create_graph as cg
import models.vehicle_models.energy_consumption as ec
import simulation.simulate_routes as sr

from pprint import pprint
def load_json(file_path):
    """Loads JSON data from a file."""
    with open(file_path, "r") as file:
        return json.load(file)

# Load battery, vehicle, and static data
static_data = load_json("models/vehicle_models/static_data.json")
vehicle_data = load_json("models/vehicle_models/vehicle_data.json")
battery_data = load_json("models/vehicle_models/battery_data.json")
map_data = load_json("./data_collection/data/large_net/fixed_large_dis_data.json")

# Load road network
road_network_file = './data_collection/data/large_net/large_edge_data.csv' 
road_df = pd.read_csv(road_network_file)

# Battery Parameters
BATTERY_CAPACITY = battery_data["Capacity"]  # Ah
OCV = battery_data["OCV"]
R_INT = battery_data["R_internal"]
MOTOR_EFF = vehicle_data["motor_eff"]

# ----------------------------------------
# Create Road Network Graph
# ----------------------------------------

graph = cg.create_osmnx_compatible_graph(road_network_file, debug=False)

route_test = (17585126, 2076171054)

# Weights for route selection
weights_dict = {
    'incline_weight': 2.28,
    'max_incline_weight': 0.88,
    'distance_weight': 5.29,
    'zero_start_weight': 15.0
}



def route_analysis(route, base_k = 0.200 ,c_rate_exp = 0.2286):

    route_obj = sr.find_route(map_data, road_df, graph, route[0], route[1], weights_dict, plot=False, weights_type='obj')
    route_dis = sr.find_route(map_data, road_df, graph, route[0], route[1], weights_dict, plot=False, weights_type='distance')


    def extract_route_data(route_output):
        """Extracts relevant energy and time data from a given route output."""
        total_distance, total_consumption, total_climb, detailed_results, current_list, climbs, distances, consumption_list= sr.return_route_data_complex(
            route_output, vehicle_data, static_data, MOTOR_EFF, battery_data
        )
        
        # Extract time per segment
        time_list = [
            data["time"]
            for key, value in detailed_results.items()
            if 'path' in key
            for _, data in value.items()
        ]
        
        return total_distance, current_list, time_list, total_consumption, consumption_list

    # Get route data
    total_distance_obj, current_list_obj, time_list_obj, total_consumption_ob, consumptions_ob = extract_route_data(route_obj)
    total_distance_dis, current_list_dis, time_list_dis, total_consumption,consumptions_dis = extract_route_data(route_dis)

    def calc_capacity_reduction(consumption):
        loss = consumption/OCV
        return loss

    def update_capacity_with_loss(current_list, consumptions, initial_capacity, OCV):
        # Initialize the capacity list with the initial capacity
        capacity_list = [initial_capacity]
        c_rates_list = []
        
        # For each step, calculate the loss and update the capacity
        for i in range(len(consumptions)):
            # Calculate capacity loss from the consumption
            loss = calc_capacity_reduction(consumptions[i])
            
            # Update the capacity by subtracting the loss
            current_capacity = capacity_list[-1] - loss
            capacity_list.append(current_capacity)
            
            # Calculate C-rate using the current capacity (not the initial one)
            c_rate = current_list[i] / current_capacity if current_capacity > 0 else float('inf')
            c_rates_list.append(c_rate)
        
        # Remove the initial capacity as it's not associated with any consumption
        capacity_list.pop(0)
        
        return capacity_list, c_rates_list


    cap_list_ob, c_rates_obj = update_capacity_with_loss(current_list_obj, consumptions_ob, BATTERY_CAPACITY, OCV)
    cap_list_dis, c_rates_dis = update_capacity_with_loss(current_list_dis, consumptions_dis, BATTERY_CAPACITY, OCV)


    # ----------------------------------------
    # Capacity Loss Calculation
    # ----------------------------------------
    

    def compute_capacity_loss(c_rate_list, time_list, k=base_k, n=c_rate_exp):
        """
        Computes total capacity loss based on an empirical degradation model.
        
        cap_loss = k * (C-rate ^ n) * cycle_fraction
        """
        cap_losses = []
        
        for c_rate, time in zip(c_rate_list, time_list):
            cycle_fraction = (time / 3600) * c_rate  # Convert time from seconds to cycles
            cap_loss = k * (c_rate ** n) * cycle_fraction
            cap_losses.append(cap_loss)

        return sum(cap_losses)

    # Calculate capacity loss
    cap_loss_obj = compute_capacity_loss(c_rates_obj, time_list_obj)
    cap_loss_dis = compute_capacity_loss(c_rates_dis, time_list_dis)



    def EOL(cap_loss, distance):

        cap_loss_per_m = cap_loss / distance

        cap_loss_per_charge = cap_loss_per_m * 45000
        # print(cap_loss_per_charge)

        EOL_expected = (BATTERY_CAPACITY*0.6)/cap_loss_per_charge
        return EOL_expected

    return EOL(cap_loss_obj, total_distance_obj) , EOL(cap_loss_dis, total_distance_dis)


