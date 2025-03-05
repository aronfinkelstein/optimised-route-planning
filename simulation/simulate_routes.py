import models.road_network.create_graph as cg
import models.vehicle_models.energy_consumption as ec
import models.weighting.weight_integration as wi
import json
import math
import pandas as pd
import random
from pprint import pprint

def find_random_route(map_data:dict, road_df:dict, graph, plot = False, weights_type = 'default'):
    '''
    Takes in a overall map, road and graph, simulates a random route and returns data for that route.
    '''
    G = wi.add_weights_to_graph(graph, weights_type)
    nodes = road_df["u"].to_list()
    random_values = random.sample(nodes, 2)
    route = cg.dijkstra(G, random_values[0], random_values[1])

    route_dict = {}
    i = 0
    for i in range(len(route)-1):
        path = cg.find_path_with_nodes(map_data, route[i], route [i + 1])
        route_dict.update(path)
    if plot:
        fig, ax = cg.plot_graph_with_routes(graph,route)
    else:
        pass

    return route_dict

def find_route(map_data:dict, road_df:dict, graph, start_node: int, end_node: int, plot = False, weights_type = 'default'):
    '''
    Takes in a overall map, road and graph, simulates a specific route and returns data for that route.
    '''

    G = wi.add_weights_to_graph(graph, weights_type)

    route = cg.dijkstra(G, start_node, end_node)
    print("---Route---")
    print(route)

    route_dict = {}
    missing_segments = []
    
    for i in range(len(route)-1):
        current_node = route[i]
        next_node = route[i + 1]        
        path = cg.find_path_with_nodes(map_data, current_node, next_node)
        
        if not path:  # If no path found between these nodes
            missing_segments.append((current_node, next_node))
            print(f"❌ No path found between nodes {current_node} and {next_node}")
        else:
            # Optionally print the first few characters of each path key
            path_keys = list(path.keys())
            # if path_keys:
            #     print(f"  First few path keys: {path_keys[:3]}")
        
        route_dict.update(path)

    if missing_segments:
        print(f"Missing {len(missing_segments)} route segments out of {len(route)-1} total segments")
        print(f"Missing segments: {missing_segments}")
    else:
        print(f"All {len(route)-1} route segments were found successfully")
        
    if plot:
        fig, ax = cg.plot_graph_with_routes(graph, route)
    
    return route_dict

def return_route_data(route_dict:dict, vehicle_data:dict, static_data:dict, motor_eff:float)->float:
    '''
    Analyses a route and returns consumption, distance, and climb data. 
    '''
    consumptions = []
    distances = []
    climbs = []
    for path, pathdata in route_dict.items():
        pprint(route_dict)
        for section, data in pathdata.items():
            if "section" in section: 
                data["velocity"] = vehicle_data["max_speed"]
                if pathdata["smooth"]:
                    data["acceleration"] = 0
                else:
                    data["acceleration"] = vehicle_data["max_acceleration"]
                tract_power = ec.physical_model(vehicle_data, static_data, data)
                batt_power = ec.battery_power_model(tract_power, motor_eff)

                energy = ec.get_edge_consumption(batt_power, data)

                distances.append(data['distance'])
                consumptions.append(energy)
                climbs.append(data['climb'])

    total_distance = sum(distances)
    total_consumption = sum(consumptions)
    total_climb = sum(climbs)

    return total_distance, total_consumption, total_climb

def return_route_data_complex(route_dict: dict, vehicle_data: dict, static_data: dict, 
                             motor_eff: float, max_motor_power: float, battery_data: dict) -> tuple:
    '''
    Analyses a route and returns consumption, distance, and climb data,
    incorporating acceleration models for more accurate energy estimation.
    
    Parameters:
    route_dict (dict): Dictionary containing route information
    vehicle_data (dict): Vehicle characteristics
    static_data (dict): Static environmental values
    motor_eff (float): Motor efficiency
    max_motor_power (float): Maximum motor power in Watts
    battery_data (dict): Battery parameters including OCV, internal resistance, and capacity
    
    Returns:
    tuple: (total_distance, total_consumption, total_climb, detailed_results)
    where detailed_results contains additional data about each segment
    '''
    OCV = battery_data["OCV"]
    R_i = battery_data["R_internal"]
    Q = battery_data["Capacity"]

    consumptions = []
    distances = []
    climbs = []
    detailed_results = {}
    
    # Target velocity (constant across the route)
    target_velocity = vehicle_data["max_speed"]
    
    # Process each path in the route
    for path, pathdata in route_dict.items():
        detailed_results[path] = {}
        
        # Starting velocity for each path
        current_velocity = 0  # Always start a new path from zero
        
        # Get all sections for this path in the correct order
        sections = []
        for section, data in pathdata.items():
            if "section" in section:
                # Create a copy of the data to avoid modifying the original
                section_data = data.copy()
                section_data["section_name"] = section
                sections.append(section_data)
        
        # Sort sections if needed (assuming they're already in order)
        
        # Process each section in the path
        for i, section_data in enumerate(sections):
            section_name = section_data["section_name"]
            detailed_results[path][section_name] = {}
            
            # Determine if this is a start from zero
            if i == 0 or not pathdata.get("smooth", False):
                start_from_zero = True
            else:
                start_from_zero = False
            
            # Reset velocity if starting from zero
            if start_from_zero:
                current_velocity = 0
                
            # Process section with acceleration model
            segment_result = ec.calculate_segment_energy_with_acceleration(
                current_velocity, target_velocity, section_data,
                vehicle_data, static_data, max_motor_power, motor_eff, OCV, R_i, Q
            )
            
            # Update current velocity for next section
            current_velocity = segment_result["final_velocity"]
            
            # Extract energy consumption - handle both return formats
            if "total_energy" in segment_result:
                energy = segment_result["total_energy"]
            else:
                energy = segment_result["energy_consumption"]
            
            # Append to results
            distances.append(section_data['distance'])
            consumptions.append(energy)
            climbs.append(section_data.get('climb', 0))
            
            # Store detailed results
            detailed_results[path][section_name] = {
                "energy": energy,
                "distance": section_data['distance'],
                "climb": section_data.get('climb', 0),
                "initial_velocity": segment_result["initial_velocity"],
                "final_velocity": segment_result["final_velocity"],
                "acceleration": segment_result["acceleration"]
            }
            
            # Additional data that may be available depending on return format
            if "total_time" in segment_result:
                detailed_results[path][section_name]["time"] = segment_result["total_time"]
            elif "time" in segment_result:
                detailed_results[path][section_name]["time"] = segment_result["time"]
            
            # Store discharge current and C-rate if available
            if "peak_discharge_current" in segment_result:
                detailed_results[path][section_name]["peak_current"] = segment_result["peak_discharge_current"]
                detailed_results[path][section_name]["peak_c_rate"] = segment_result["peak_c_rate"]
                detailed_results[path][section_name]["avg_current"] = segment_result["avg_discharge_current"]
                detailed_results[path][section_name]["avg_c_rate"] = segment_result["avg_c_rate"]
            elif "discharge_current" in segment_result:
                detailed_results[path][section_name]["current"] = segment_result["discharge_current"]
                detailed_results[path][section_name]["c_rate"] = segment_result["c_rate"]
            
            # Store phase information if available
            if "acceleration_phase" in segment_result:
                detailed_results[path][section_name]["acceleration_phase"] = segment_result["acceleration_phase"]
                detailed_results[path][section_name]["constant_phase"] = segment_result["constant_phase"]
            
            # Store target velocity achievement
            detailed_results[path][section_name]["reached_target"] = segment_result.get("reached_target", False)
    
    # Calculate totals
    total_distance = sum(distances)
    total_consumption = sum(consumptions)
    total_climb = sum(climbs)
    
    # Calculate additional summary metrics
    detailed_results["summary"] = {
        "total_distance": total_distance,
        "total_consumption": total_consumption,
        "total_climb": total_climb,
        "wh_per_km": (total_consumption / total_distance * 1000) if total_distance > 0 else 0,
        "wh_per_climb_m": (total_consumption / total_climb) if total_climb > 0 else 0
    }

    # Return both the basic metrics and detailed results
    return total_distance, total_consumption, total_climb, detailed_results