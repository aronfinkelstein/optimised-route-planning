import osmnx as ox
import requests
import pandas as pd
import graph as gr
import numpy as np

central_point = (51.456127, -2.608071) #latitude, longitude

G = ox.graph_from_point(central_point, dist=500, network_type='bike')

nodes = ox.graph_to_gdfs(G, edges=False)
nodes['osmid'] = nodes.index
edges = ox.graph_to_gdfs(G, nodes=False)

def get_elevation(lat, lon):
    """
    Hits the open top data api to get elevation data for a specific point
    # """
    # url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"

    url = f"https://api.opentopodata.org/v1/aster30m?locations={lat},{lon}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "results" in data:
            return data['results'][0]['elevation']
        else:
            return None
    else:
        print(f"Error fetching elevation: {response.status_code}")
        return None
    
def get_elevation_diff(u,v):
    """
    Gets the elevation difference between two osmid points
    """
    u_lat, u_lon = nodes.loc[u, ['y', 'x']]
    v_lat, v_lon = nodes.loc[v, ['y', 'x']]
    
    start_el = get_elevation(u_lat, u_lon)
    end_el = get_elevation(v_lat, v_lon)

    if start_el is not None and end_el is not None:
        return (start_el - end_el)
    else:
        print("Error: Could not fetch elevation data for one or both nodes.")
        return None
    
def save_node_geometries_to_csv():
    '''
    saves the node data to a csv
    '''
    nodes['latitude'] = nodes['geometry'].apply(lambda geom: geom.y if geom is not None else None)
    nodes['longitude'] = nodes['geometry'].apply(lambda geom: geom.x if geom is not None else None)

    nodes[['osmid', 'latitude', 'longitude']].to_csv('../data/noe_data.csv', index=False)
    print("Nodes saved to 'nodes_geometries.csv'.")

def save_edge_data_to_csv(edge_data):
    '''
    saves the edge data
    '''
    edge_data.to_csv('edge_data.csv', index=True)
    # print("saved edges to csv")

def edge_climbs():
    climbs = []

    for index, row in edges['osmid'].iterrows():
        u = row['u'] 
        v = row['v']

        u_lat, u_lon = nodes.loc[u, ['y', 'x']]  # Latitude, Longitude for node u
        v_lat, v_lon = nodes.loc[v, ['y', 'x']]  # Latitude, Longitude for node v

        # Get the elevation difference for the current edge
        elevation_diff = get_elevation_diff(u_lat, u_lon, v_lat, v_lon)

        # Store the result (osmid pair and the elevation difference)
        climbs.append({
            'u_osmid': u,
            'v_osmid': v,
            'elevation_diff': elevation_diff
        })

    climbs_df = pd.DataFrame(climbs)

    print(climbs_df.head())

def split_linestring(linestring: str):
    coords_str = linestring.replace("LineString (", "").replace(")", "")
    coords_pairs = coords_str.split(", ")
    coords_tuples = [tuple(map(float, pair.split())) for pair in coords_pairs]
    return coords_tuples

def get_way_elevation():
    ways_df = pd.read_csv('../data/edge_data.csv')
    ways_coords = ways_df['geometry'].to_list()
    print(ways_coords)
    for coord in ways_coords:
        print(coord)
        coords = split_linestring(coord)
        print(coords)
        for pair in coords:
            print(get_elevation(pair[1], pair[0]))

def find_edge_by_osmid(graph):
    ways_df = pd.read_csv('../data/edge_data.csv')
    edge_ids = ways_df['osmid'].to_list()
    graph_ids = []
    for id in edge_ids:
        for u, v, key, data in graph.edges(keys=True, data=True):
            # Check if the osmid matches (handles single or list osmids)
            if "osmid" in data:
                if isinstance(data["osmid"], list):
                    if id in data["osmid"]:
                        return u, v
                elif data["osmid"] == id:
                    return u, v
        graph_ids.append({
                'u_osmid': u,
                'v_osmid': v,
                'edge_osmid': id
            })
    return graph_ids

if __name__ == "__main__":
    pass