def calculate_path_weight(path_data, weights_dict):
    """
    Calculates a weight for a path segment based on EV-relevant factors.
    Enhanced to create more varied weights for better path differentiation.
    Higher weights indicate less desirable paths for an electric vehicle.
    
    Parameters:
    path_data (dict): Dictionary containing path information with keys:
        'average_incline': Average incline in degrees
        'max_incline': Maximum incline in degrees
        'distance': Distance in meters
        'zero_start': Boolean indicating if vehicle starts from zero velocity
    
    Returns:
    float: Calculated weight for the path segment
    """
    # Extract relevant features
    avg_incline = float(path_data['average_incline'])  # in degrees
    max_incline = float(path_data['max_incline'])      # in degrees
    distance = float(path_data['distance'])            # in meters
    zero_start = path_data['zero_start']
    
    # Base distance effect - critical for differentiation even with zero inclines
    # This creates significant variation even for flat paths of different lengths
    base_distance_effect = distance / 10  # Much higher impact than before
    
    # ENHANCED EXPONENTIAL SCALING for inclines
    # Using a lower divisor and higher exponent to create bigger differences
    # Add a base value of 1.0 to ensure even tiny inclines have some effect
    avg_incline_effect = 1.0 + pow(abs(avg_incline) / 3, 2.5)  # More aggressive scaling
    
    # Even more aggressive scaling for maximum inclines
    # Lower divisor (2 instead of 4) makes small max inclines have bigger impact
    max_incline_effect = 1.0 + pow(abs(max_incline) / 2, 3.0)  # Much steeper scaling
    
    # Direction matters: uphill is worse than downhill for EVs
    # Add direction penalty for positive inclines (uphill)
    direction_factor = 1.5 if avg_incline > 0 else 0.8  # Uphill is 1.5x worse than downhill
    
    # Much higher penalty for non-zero starts
    # This should significantly affect routes with many stops
    zero_start_factor = 1.0 if zero_start else 3.5  # More dramatic difference
    
    # HIGHLY DIFFERENTIATED weights with increased base values
    incline_weight = weights_dict["incline_weight"]     # Increased from 3.0
    max_incline_weight = weights_dict["max_incline_weight"]  # Increased from 4.0
    distance_weight = weights_dict["distance_weight"]   # Base impact for distance
    zero_start_weight = weights_dict["zero_start_weight"]   # Increased from 2.0
    
    # Calculate final weight with dramatically different scaling
    # Using multiplication in some places to create more variation
    # The multiplication of incline effects creates exponential differences
    incline_component = (incline_weight * avg_incline_effect * direction_factor)
    max_incline_component = (max_incline_weight * max_incline_effect)
    
    # This formula creates much more varied weights
    final_weight = (
        incline_component +
        max_incline_component +
        distance_weight * base_distance_effect +
        zero_start_weight * zero_start_factor
    )
    
    # Apply logarithmic scaling to compensate for very large values
    # while still maintaining significant differences
    if final_weight > 50:
        final_weight = 50 + 20 * (final_weight - 50) ** 0.5
    
    # Ensure minimum weight is higher than default (1.0) to force differentiation
    # Also raise the maximum to allow more extreme values for truly bad paths
    final_weight = max(1.5, min(200.0, final_weight))
    
    return final_weight