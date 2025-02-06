import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt

# Load edge data from CSV file
edge_df = pd.read_csv('../data/random_weight_edge.csv')  # Adjust path if needed

# Initialize graphs
G = nx.DiGraph()  # Weighted graph
F = nx.DiGraph()  # Unweighted graph

# Add edges to the graphs
for _, row in edge_df.iterrows():
    source = int(row['u'])
    target = int(row['v'])
    length = float(row['weights'])  # Use raw weight without rounding for accuracy

    # Add to weighted graph
    G.add_edge(source, target, length=length)

    # Add to unweighted graph (ignoring weights)
    F.add_edge(source, target)

# # Debugging: Visualize the graph structure
# print("Weighted Graph (G):", G.edges(data=True))
# print("Unweighted Graph (F):", F.edges(data=True))


def dijkstra(start_node:int, target_node:int) -> list:
    weighted_path = nx.shortest_path(G, source=start_node, target=target_node, weight='length')
    return weighted_path

def a_star(start_node:int, target_node:int) -> list:
    weighted_path = nx.astar_path(G, source=start_node, target=target_node, weight='length')
    return weighted_path

def debug():
    # Define source and target nodes
    source_node = 1022548104
    target_node = 11865591910
    # Calculate shortest path for the weighted graph
    try:
        weighted_path = nx.shortest_path(G, source=source_node, target=target_node, weight='length')
        weighted_path_length = nx.shortest_path_length(G, source=source_node, target=target_node, weight='length')
        print("\nWeighted Path:", weighted_path)
        print("Weighted Path Length:", weighted_path_length)
    except nx.NetworkXNoPath:
        print("\nNo path found in weighted graph.")

    # Calculate shortest path for the unweighted graph
    try:
        unweighted_path = nx.shortest_path(F, source=source_node, target=target_node)
        unweighted_path_length = nx.shortest_path_length(F, source=source_node, target=target_node)
        print("\nUnweighted Path:", unweighted_path)
        print("Unweighted Path Length:", unweighted_path_length)
    except nx.NetworkXNoPath:
        print("\nNo path found in unweighted graph.")

    # Compare paths
    if 'weighted_path' in locals() and 'unweighted_path' in locals():
        if weighted_path == unweighted_path:
            print("\nThe shortest paths are the same for both weighted and unweighted graphs.")
        else:
            print("\nThe shortest paths are different for weighted and unweighted graphs.")


    # Debugging: Calculate the total weight of the weighted path
    if 'weighted_path' in locals():
        total_weight = sum(G[u][v]['length'] for u, v in zip(weighted_path[:-1], weighted_path[1:]))
        print("\nTotal Weight of the Weighted Path:", total_weight)

    # Debugging: Calculate the "unweighted weight" (number of edges)
    if 'unweighted_path' in locals():
        total_unweighted_weight = len(unweighted_path) - 1  # Unweighted = number of edges
        print("Number of Edges in the Unweighted Path:", total_unweighted_weight)

    # Visualize one of the graphs (optional)
    plt.figure(figsize=(10, 6))
    nx.draw_spring(G, with_labels=True, node_size=500, node_color='lightblue', font_size=10)
    plt.title("Weighted Graph Visualization")
    plt.show()


