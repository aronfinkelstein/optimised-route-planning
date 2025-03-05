'''
Integrating weight data with general csv data.
'''
import random
import models.weighting.weight_model as wm


def add_weights_to_graph(G, weights_type = 'default', default_weight=1.0):
    """
    Add weights to a graph based on an existing attribute or a default value.
    
    Parameters:
    -----------
    G : NetworkX graph
        The graph to modify
    weight_attribute : str
        Name of the attribute to use as weight
    default_weight : float
        Default weight value if attribute is missing
    """

    for u, v, k, data in G.edges(keys=True, data=True):
        if weights_type == 'default':
            G[u][v][k]['weight'] = default_weight
        # if weights_type == 'random':
        #     G[u][v][k]['weight'] = random.random()
        if weights_type == 'random':
            distance = data.get('length', 1.0)
            
            # Set alpha to 1.0 since we're only considering distance
            # and set other parameters to 0
            G[u][v][k]['weight'] = wm.calculate_path_weight(
                distance=distance,
                energy=0,  # Placeholder value, not used
                c_rate=0,  # Placeholder value, not used
                alpha=0.5,
                beta=0.0,
                gamma=0.0
            )
    
    return G