import networkx as nx
import pandas as pd
import osmnx as ox
from shapely import wkt

def create_bidirectional_graph(csv_path):
    '''
    Create a graph with bidirectional edges to ensure connectivity
    '''
    # Load the edge data from CSV
    edge_df = pd.read_csv(csv_path)
    
    # Create a MultiDiGraph
    G = nx.MultiDiGraph()
    
    # Convert geometry strings to Shapely geometries
    if 'geometry' in edge_df.columns:
        edge_df['geometry'] = edge_df['geometry'].apply(lambda x: wkt.loads(x) if isinstance(x, str) else None)
    
    # Add nodes with coordinates
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
        
        # Add the reverse edge to make it bidirectional
        # You might want to modify this part depending on your needs
        G.add_edge(target, source, key=key, **edge_attrs)
    
    # Set graph crs attribute for osmnx plotting
    G.graph['crs'] = 'EPSG:4326'
    
    return G

def create_osmnx_compatible_graph(csv_path, debug=False):
    '''
    Initialise a graph based on route data
    '''
    # Load the edge data from CSV
    edge_df = pd.read_csv(csv_path)
    
    if debug:
        print(f"Loaded {len(edge_df)} edges from CSV")
        print(f"CSV columns: {edge_df.columns.tolist()}")
        # Print a sample edge
        if len(edge_df) > 0:
            print("Sample edge data:")
            print(edge_df.iloc[0])
    
    # Create a MultiDiGraph (OSMnx requires this type)
    G = nx.MultiDiGraph()
    
    # Convert geometry strings to Shapely geometries
    if 'geometry' in edge_df.columns:
        edge_df['geometry'] = edge_df['geometry'].apply(lambda x: wkt.loads(x) if isinstance(x, str) else None)
        
        if debug:
            null_geom_count = edge_df['geometry'].isna().sum()
            print(f"Edges with null geometry: {null_geom_count} ({null_geom_count/len(edge_df)*100:.1f}%)")
    
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
    
    if debug:
        print(f"Collected coordinates for {len(nodes)} unique nodes")
    
    # Add nodes to the graph
    for node_id, attrs in nodes.items():
        G.add_node(node_id, **attrs)
    
    # Add edges to the graph with key and geometry
    edge_count = 0
    weight_attrs = []
    for _, row in edge_df.iterrows():
        source = int(row['u'])
        target = int(row['v'])
        key = 0 if 'key' not in row else int(row['key'])
        
        # Create edge attributes dictionary
        edge_attrs = {k: v for k, v in row.items() if k not in ['u', 'v', 'key']}
        
        # Add edge with all attributes
        G.add_edge(source, target, key=key, **edge_attrs)
        edge_count += 1
        
        # Track potential weight attributes
        if edge_count == 1:
            weight_attrs = [k for k, v in edge_attrs.items() if isinstance(v, (int, float))]
    
    if debug:
        print(f"Added {edge_count} edges to the graph")
        print(f"Potential weight attributes: {weight_attrs}")
        
        # Check bidirectionality
        bidirectional_count = 0
        for u, v in G.edges():
            if G.has_edge(v, u):
                bidirectional_count += 1
        print(f"Bidirectional edges: {bidirectional_count} ({bidirectional_count/G.number_of_edges()*100:.1f}%)")
    
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
        fig, ax = ox.plot_graph_routes(G, routes, route_colors=route_colors, bgcolor='w', edge_color='#999999', node_color='#999999',
                                     node_size=10, edge_linewidth=1)
    
    return fig, ax

def plot_graph_with_colour_sroute(G, route, route_color='red', background='w'):
    """
    Plot a graph with a route in a single color
    
    Parameters:
    -----------
    G : networkx.MultiDiGraph
        The graph to plot
    route : list
        Route as a list of nodes
    route_color : str, optional
        Color for the route (default 'red')
    background : str, optional
        Background color (default 'w' for white)
    """
    import matplotlib.pyplot as plt
    import osmnx as ox
    
    # Create the figure and axis
    fig, ax = ox.plot_graph(G, show=False, close=False, 
                           bgcolor=background, edge_color='#CCCCCC', 
                           node_color='#CCCCCC', node_size=5)
    
    # Create edge pairs from the route nodes
    route_edges = list(zip(route[:-1], route[1:]))
    
    # Plot each edge with the same color
    for u, v in route_edges:
        # First try to find if this edge exists in the graph
        if G.has_edge(u, v):
            # For MultiDiGraph there might be multiple edges
            edge_data = None
            
            # Try to find an edge with geometry
            for key, data in G.get_edge_data(u, v).items():
                if 'geometry' in data:
                    edge_data = data
                    break
            
            # If we found an edge with geometry
            if edge_data and 'geometry' in edge_data:
                xs, ys = edge_data['geometry'].xy
                ax.plot(xs, ys, color=route_color, linewidth=4, alpha=0.8, zorder=3)
                continue
        
        # If no geometry found, use straight line between nodes
        x_u, y_u = G.nodes[u]['x'], G.nodes[u]['y']
        x_v, y_v = G.nodes[v]['x'], G.nodes[v]['y']
        ax.plot([x_u, x_v], [y_u, y_v], color=route_color, linewidth=4, alpha=0.8, zorder=3)
    
    # Plot nodes over the edges
    node_Xs = [G.nodes[node]['x'] for node in route]
    node_Ys = [G.nodes[node]['y'] for node in route]
    ax.scatter(node_Xs, node_Ys, s=30, c='black', zorder=4)
    
    plt.tight_layout()
    return fig, ax

def dijkstra(G, start_node:int, target_node:int) -> list:
    weighted_path = nx.dijkstra_path(G, source=start_node, target=target_node, weight='weight')
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