import pandas as pd
import numpy as np
import re

def classify_stop_start_edges(csv_file_path):
    """
    Analyzes OSM edge data and returns a list of OSMIDs with a flag indicating
    whether each edge is likely to involve stop-start driving.
    
    Args:
        csv_file_path (str): Path to the CSV file containing OSM edge data
        
    Returns:
        DataFrame: Contains OSMIDs and stop_start flag with confidence score
    """
    # Load the CSV data
    df = pd.read_csv(csv_file_path)
    print(f"Loaded {len(df)} edges from the CSV file")
    
    # Create a copy to add our classification
    result_df = df[['osmid']].copy()
    result_df['has_stop_start'] = False
    result_df['confidence'] = 0  # Add confidence score (0-10)
    
    # 1. First, identify intersection nodes
    all_nodes = pd.concat([df['u'], df['v']]).reset_index(drop=True)
    node_counts = all_nodes.value_counts()
    
    # Create a set to store potential stop-start nodes
    stop_start_nodes = set()
    node_confidence = {}  # Dictionary to store confidence scores for nodes
    
    # 1.1 Complex intersections (nodes with many connecting edges)
    complex_threshold = 4  # More selective: 4+ roads meeting (was 3)
    complex_intersections = node_counts[node_counts >= complex_threshold].index.tolist()
    
    for node in complex_intersections:
        stop_start_nodes.add(node)
        # Assign confidence based on number of connections (max 3 points)
        connections = node_counts[node]
        node_confidence[node] = min(connections - 2, 3)
    
    print(f"Found {len(complex_intersections)} complex intersection nodes")
    
    # 2. Check for junction tags
    junction_nodes = set()
    if 'junction' in df.columns and df['junction'].notna().any():
        junction_edges = df[df['junction'].notna()]
        junction_nodes = set(pd.concat([junction_edges['u'], junction_edges['v']]).unique())
        
        for node in junction_nodes:
            stop_start_nodes.add(node)
            node_confidence[node] = node_confidence.get(node, 0) + 2  # +2 for junction tag
    
    print(f"Found {len(junction_nodes)} nodes with junction tags")
    
    # 3. Check for highway hierarchy transitions
    transition_nodes = set()
    if 'highway' in df.columns:
        # Define hierarchy of roads
        highway_hierarchy = {
            'motorway': 1,
            'trunk': 2,
            'primary': 3,
            'secondary': 4,
            'tertiary': 5,
            'unclassified': 6,
            'residential': 7,
            'service': 8,
            'track': 9,
            'path': 10,
            'footway': 11,
            'cycleway': 11,
            'steps': 11
        }
        
        # Create a dictionary mapping nodes to highway types
        node_highway_types = {}
        
        # Populate the dictionary
        for _, row in df.iterrows():
            if pd.isna(row['highway']):
                continue
                
            # Sometimes OSM has highway types as lists, handle both cases
            if isinstance(row['highway'], str) and '[' in row['highway']:
                try:
                    highway_types = eval(row['highway'])
                    if isinstance(highway_types, list):
                        highway_type = highway_types[0] if highway_types else 'unknown'
                    else:
                        highway_type = str(row['highway'])
                except:
                    highway_type = str(row['highway'])
            else:
                highway_type = str(row['highway'])
            
            # Add highway type to node's list
            if row['u'] not in node_highway_types:
                node_highway_types[row['u']] = []
            if row['v'] not in node_highway_types:
                node_highway_types[row['v']] = []
                
            node_highway_types[row['u']].append(highway_type)
            node_highway_types[row['v']].append(highway_type)
        
        # Find nodes with significant highway transitions
        for node, highway_types in node_highway_types.items():
            unique_types = set(highway_types)
            
            if len(unique_types) > 1:
                # Calculate the range of highway hierarchy
                hierarchy_values = [highway_hierarchy.get(htype.lower(), 99) 
                                    for htype in unique_types if isinstance(htype, str)]
                
                if hierarchy_values and max(hierarchy_values) - min(hierarchy_values) >= 3:  # More selective: bigger hierarchy gap
                    transition_nodes.add(node)
                    
                    # Add to confidence based on hierarchy difference
                    hierarchy_diff = max(hierarchy_values) - min(hierarchy_values)
                    conf_score = min(2, hierarchy_diff - 2)  # Max +2 for hierarchy difference
                    node_confidence[node] = node_confidence.get(node, 0) + conf_score
    
    print(f"Found {len(transition_nodes)} nodes with significant highway transitions")
    stop_start_nodes.update(transition_nodes)
    
    # 4. Check for speed transitions
    speed_transition_nodes = set()
    if 'maxspeed' in df.columns:
        # Extract numeric speed values where possible
        def extract_speed(speed_str):
            if pd.isna(speed_str):
                return None
            if isinstance(speed_str, (int, float)):
                return float(speed_str)
            # Extract numeric part from strings like "30 mph" or "50 km/h"
            match = re.search(r'(\d+)', str(speed_str))
            if match:
                return float(match.group(1))
            return None
            
        df['speed_value'] = df['maxspeed'].apply(extract_speed)
        
        # Create a dictionary of nodes to their connected speed values
        node_speeds = {}
        
        # Populate the dictionary
        for _, row in df.iterrows():
            if pd.isna(row['speed_value']):
                continue
                
            if row['u'] not in node_speeds:
                node_speeds[row['u']] = []
            if row['v'] not in node_speeds:
                node_speeds[row['v']] = []
                
            node_speeds[row['u']].append(row['speed_value'])
            node_speeds[row['v']].append(row['speed_value'])
        
        # Find nodes with significant speed differences
        for node, speeds in node_speeds.items():
            if len(speeds) > 1:
                # Calculate the difference between max and min speed
                speed_diff = max(speeds) - min(speeds)
                if speed_diff >= 15:  # More selective: 15+ mph/km/h difference (was 10)
                    speed_transition_nodes.add(node)
                    
                    # Add to confidence based on speed difference
                    conf_score = min(2, speed_diff / 10)  # Max +2 for big speed differences
                    node_confidence[node] = node_confidence.get(node, 0) + conf_score
    
    print(f"Found {len(speed_transition_nodes)} nodes with significant speed transitions")
    stop_start_nodes.update(speed_transition_nodes)
    
    # 5. Apply the node classifications to edges
    for i, row in df.iterrows():
        u_node, v_node = row['u'], row['v']
        
        # Edge has stop-start if either endpoint is a stop-start node
        if u_node in stop_start_nodes or v_node in stop_start_nodes:
            result_df.loc[i, 'has_stop_start'] = True
            
            # Set confidence to the higher of the two node confidence scores
            u_conf = node_confidence.get(u_node, 0)
            v_conf = node_confidence.get(v_node, 0)
            result_df.loc[i, 'confidence'] = max(u_conf, v_conf)
    
    # 6. Normalize confidence to 0-10 scale and round to 1 decimal place
    max_possible = 7  # Max points possible from all criteria
    result_df['confidence'] = (result_df['confidence'] / max_possible * 10).round(1)
    
    # Only mark as stop-start if confidence exceeds a minimum threshold
    confidence_threshold = 5.0  # More selective: Must have reasonable confidence
    result_df.loc[result_df['confidence'] < confidence_threshold, 'has_stop_start'] = False
    
    # 7. Calculate some summary statistics
    total_edges = len(result_df)
    stop_start_edges = result_df['has_stop_start'].sum()
    
    print(f"\nResults:")
    print(f"Total edges: {total_edges}")
    print(f"Edges with stop-start driving: {stop_start_edges} ({stop_start_edges/total_edges*100:.1f}%)")
    
    return result_df
