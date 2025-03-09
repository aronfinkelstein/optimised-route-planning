'''
Integrating weight data with general csv data.
'''
import random
import numpy as np
import models.weighting.weight_model as wm


def process_path_weight(path: dict) -> dict:
    # Extract section data in a single list comprehension
    section_data = [(items["avg_incline_angle"], items["distance"]) 
                    for key, items in path.items() if 'section' in key]
    
    # Unpack the section data only if there are sections
    if section_data:
        incline_angles, distances = zip(*section_data)
    else:
        incline_angles, distances = [], []
    
    return {
        'average_incline': np.average(incline_angles) if incline_angles else 0,
        'max_incline': max(incline_angles) if incline_angles else 0,
        'distance': sum(distances),
        'zero_start': path.get('smooth', False)  # Use get with default value
    }
def add_weights_to_graph(G, map_data:dict,weights_dict, weights_type='default', default_weight=1.0, save_weights = False):
    """
    Add weights to a graph based on an existing attribute or a default value.
    Optionally saves all weights to a JSON file for analysis.
    """
    import json
    import numpy as np
    import models.weighting.weight_model as wm
    
    # print(f'Weight function running with type: {weights_type}')
    total_edges = G.number_of_edges()
    custom_weights = 0
    attribute_weights = 0
    objective_function_calls = 0
    
    # Clear all existing weights first to ensure we're starting fresh
    for u, v, k, data in G.edges(keys=True, data=True):
        if 'weight' in data:
            del data['weight']
    
    # Create a list to store all edge weights
    all_weights = []
    
    for u, v, k, data in G.edges(keys=True, data=True):
        weight_assigned = False
        edge_record = {
            'source': u,
            'target': v,
            'key': k,
            'weight_type': weights_type,
            'length': data.get('length', 0),
            'has_custom_data': False
        }
        
        # First try to get weight from map_data (for specific paths)
        for path, value in map_data.items():
            if 'nodes' in value and len(value['nodes']) >= 2:
                if u == value['nodes'][0] and v == value['nodes'][1]:
                    # Custom path data found
                    edge_record['has_custom_data'] = True
                    edge_record['path_key'] = path
                    
                    # Process the path
                    results = process_path_weight(value)
                    edge_record['avg_incline'] = results['average_incline']
                    edge_record['max_incline'] = results['max_incline']
                    edge_record['distance'] = results['distance']
                    edge_record['zero_start'] = results['zero_start']
                    
                    if weights_type == 'distance':
                        weight = results['distance']
                        edge_record['weight_source'] = 'custom_distance'
                        
                    elif weights_type == 'objective':
                        weight = wm.calculate_path_weight(results, weights_dict)
                        objective_function_calls += 1
                        edge_record['weight_source'] = 'custom_objective'
                        
                    else:
                        # Default
                        weight = default_weight
                        edge_record['weight_source'] = 'custom_default'
                    
                    G[u][v][k]['weight'] = weight
                    edge_record['weight'] = weight
                    weight_assigned = True
                    custom_weights += 1
                    break
        
        # If no custom weight was assigned, use length attribute or default
        if not weight_assigned:
            if weights_type == 'distance' and 'length' in data:
                weight = data['length']
                edge_record['weight_source'] = 'attribute_distance'
                
            elif weights_type == 'objective' and 'length' in data:
                simple_path_data = {
                    'average_incline': 0,
                    'max_incline': 0,
                    'distance': data['length'],
                    'zero_start': True
                }
                
                weight = wm.calculate_path_weight(simple_path_data, weights_dict)
                objective_function_calls += 1
                edge_record['weight_source'] = 'attribute_objective'
                edge_record['avg_incline'] = 0
                edge_record['max_incline'] = 0
                edge_record['zero_start'] = True
                
            else:
                weight = default_weight
                edge_record['weight_source'] = 'default'
            
            G[u][v][k]['weight'] = weight
            edge_record['weight'] = weight
            attribute_weights += 1
        
        all_weights.append(edge_record)
    
    # Print summary statistics
    # print(f"Weight type: {weights_type}")
    # print(f"Edges with custom weights from map_data: {custom_weights}/{total_edges}")
    # print(f"Edges with attribute-based weights: {attribute_weights}/{total_edges}")
    # print(f"Total objective function calls: {objective_function_calls}")
    
    # Analyze weight distribution
    if total_edges > 0:
        weights = [data.get('weight', 0) for _, _, _, data in G.edges(keys=True, data=True)]
        min_weight = min(weights)
        max_weight = max(weights)
        avg_weight = sum(weights) / len(weights)
        # print(f"Weight distribution - Min: {min_weight:.4f}, Max: {max_weight:.4f}, Avg: {avg_weight:.4f}")
    
    if save_weights:
        # Save to JSON file if output_file is specified
        output_file = f'{weights_type}.json'
        with open(output_file, 'w') as f:
            json.dump({
                'weights_type': weights_type,
                'total_edges': total_edges,
                'custom_weights': custom_weights,
                'attribute_weights': attribute_weights,
                'edges': all_weights
            }, f, indent=2)
        
        print(f"Weights saved to {output_file}")
    
    return G