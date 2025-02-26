def calculate_path_weight(distance, energy, c_rate, alpha=0.33, beta=0.33, gamma=0.33):
    """
    Calculate a weighted score for a path based on multiple objectives.
    
    Parameters:
    -----------
    distance : float
        Total distance of the path
    energy : float
        Energy consumption for the path
    c_rate : float
        Average C-rate for the path
    alpha, beta, gamma : float
        Weighting factors for each objective (should sum to 1)
        
    Returns:
    --------
    float
        Combined weight score (lower is better)
    """
    # Normalize the values (optional, but recommended)
    # For now, we'll assume these are already normalized
    
    # Calculate weighted sum
    weight = alpha * distance + beta * energy + gamma * c_rate
    
    return weight