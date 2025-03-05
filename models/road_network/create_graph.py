import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import osmnx as ox
from shapely import wkt
import geopandas as gpd

def create_osmnx_compatible_graph(csv_path):
    '''
    Initialise a graph based on route data
    '''
    # Load the edge data from CSV
    edge_df = pd.read_csv(csv_path)
    
    # Create a MultiDiGraph (OSMnx requires this type)
    G = nx.MultiDiGraph()
    
    # Convert geometry strings to Shapely geometries
    if 'geometry' in edge_df.columns:
        edge_df['geometry'] = edge_df['geometry'].apply(lambda x: wkt.loads(x) if isinstance(x, str) else None)
    
    # First pass: collect all nodes and their coordinates
    nodes = {}
    for _, row in edge_df.iterrows():
        source = int(row['u'])
        target = int(row['v'])
        
        # Extract coordinates from geometry if available
        if 'geometry' in edge_df.columns and row['geometry'] is not None:
            geom = row['geometry']
            # Add source node
            if source not in nodes:
                nodes[source] = {'x': geom.coords[0][0], 'y': geom.coords[0][1]}
            
            # Add target node
            if target not in nodes:
                nodes[target] = {'x': geom.coords[-1][0], 'y': geom.coords[-1][1]}
    
    # Add nodes to the graph
    for node_id, attrs in nodes.items():
        G.add_node(node_id, **attrs)
    
    # Add edges to the graph with key and geometry
    for _, row in edge_df.iterrows():
        source = int(row['u'])
        target = int(row['v'])
        key = 0 if 'key' not in row else int(row['key'])
        
        # Create edge attributes dictionary
        edge_attrs = {k: v for k, v in row.items() if k not in ['u', 'v', 'key']}
        
        # Add edge with all attributes
        G.add_edge(source, target, key=key, **edge_attrs)
    
    # Set graph crs attribute for osmnx plotting
    G.graph['crs'] = 'EPSG:4326'
    
    return G

def plot_graph_with_routes(G, route1=None, route2=None):
    """
    Plot the graph and optionally one or two routes on it
    """
    if route1 is None and route2 is None:
        # Just plot the graph
        fig, ax = ox.plot_graph(G, node_size=10, edge_linewidth=1)
    else:
        # Prepare routes
        routes = []
        route_colors = []
        
        if route1 is not None:
            routes.append(route1)
            route_colors.append('r')
        
        if route2 is not None:
            routes.append(route2)
            route_colors.append('b')
        
        # Plot graph with routes
        fig, ax = ox.plot_graph_routes(G, routes, route_colors=route_colors, 
                                     node_size=10, edge_linewidth=1)
    
    return fig, ax

def dijkstra(G, start_node:int, target_node:int) -> list:
    weighted_path = nx.shortest_path(G, source=start_node, target=target_node, weight='weight')
    return weighted_path

def find_ways(route:list, road_df)-> list:
    nodes = []
    for node in road_df['u'].to_list(), road_df['v'].to_list():
        nodes.append(node)

    route_osmids = []
    route_data = {}
    for i in range(len(route) - 1):
        u = route[i]
        v = route[i + 1]

        result = road_df[(road_df['u'] == u) & (road_df['v'] == v)]
        route_osmids.append(result['osmid'].iloc[0])
        route_data[f'path{i+1}'] = result


    return route_osmids, route_data

def find_path_with_nodes(paths_dict, node1, node2):
    """
    Search through a dictionary of paths to find keys where the 'nodes' value
    contains the two specified integers (node1 and node2) in the exact order.
    """
    matching_paths = {}
    checked_paths = 0
    nodes_found = 0
    
    # Convert node1 and node2 to integers just to be safe
    node1 = int(node1)
    node2 = int(node2)
    
    for path_key, path_data in paths_dict.items():
        checked_paths += 1
        
        # Skip if the path doesn't have a 'nodes' key
        if 'nodes' not in path_data:
            continue
            
        nodes = path_data['nodes']
        
        # Ensure nodes is accessed correctly
        if not isinstance(nodes, list) and not isinstance(nodes, tuple):
            print(f"Warning: 'nodes' in {path_key} is not a list or tuple: {type(nodes)}")
            continue
            
        if len(nodes) < 2:
            print(f"Warning: 'nodes' in {path_key} has fewer than 2 elements: {nodes}")
            continue
            
        # Convert nodes to integers for comparison if they aren't already
        node_0 = int(nodes[0])
        node_1 = int(nodes[1])
        
        # Check exact match of nodes in correct order for directed graph
        if node1 == node_0 and node2 == node_1:
            matching_paths[f'{path_key}'] = path_data
            nodes_found += 1
    
    # print(f"Checked {checked_paths} paths, found {nodes_found} matches for {node1}->{node2}")
    return matching_paths