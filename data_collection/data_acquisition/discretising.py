import math

def discretise_all_sections(road_data, max_length=20.0):
    """
    Finds and replaces sections longer than max_length with multiple shorter sections.
    Works with data structure where sections are nested within paths.
    Sets 'climb' to False for all newly created sections.
    
    Args:
        road_data: Dictionary containing paths, each containing sections
        max_length: Maximum length of each section in meters
        
    Returns:
        Updated road_data with long sections replaced by shorter ones
    """
    new_road_data = {}
    
    # Iterate through each path
    for path_id, path_content in road_data.items():
        new_path_content = {}
        
        # Process each item in the path content
        for key, value in path_content.items():
            # If it's a section (has 'distance' and 'coords')
            if isinstance(value, dict) and 'distance' in value and 'coords' in value:
                section = value
                
                # If section is shorter than max_length, keep it as is
                if section['distance'] <= max_length:
                    new_path_content[key] = section
                    continue
                
                # Calculate how many subsections we need
                distance = section['distance']
                num_subsections = math.ceil(distance / max_length)
                
                # Get coordinates
                coords = section['coords']
                start_lon, start_lat = coords[0], coords[1]
                end_lon, end_lat = coords[2], coords[3]
                
                # Create new subsections
                for i in range(num_subsections):
                    # Calculate position along the line
                    start_ratio = i / num_subsections
                    end_ratio = (i + 1) / num_subsections
                    
                    # Calculate new coordinates
                    sub_start_lon = start_lon + start_ratio * (end_lon - start_lon)
                    sub_start_lat = start_lat + start_ratio * (end_lat - start_lat)
                    sub_end_lon = start_lon + end_ratio * (end_lon - start_lon)
                    sub_end_lat = start_lat + end_ratio * (end_lat - start_lat)
                    
                    # Calculate subsection distance
                    sub_distance = distance / num_subsections
                    
                    # Create new section ID
                    if i == 0:
                        new_section_id = key
                    else:
                        new_section_id = f"{key}_{i}"
                    
                    # Create the new section
                    new_section = section.copy()
                    new_section['coords'] = [sub_start_lon, sub_start_lat, sub_end_lon, sub_end_lat]
                    new_section['distance'] = sub_distance
                    
                    # Set climb to False for these new sections
                    new_section['climb'] = False
                    
                    # Also set avg_incline_angle to False if it exists
                    if 'avg_incline_angle' in new_section:
                        new_section['avg_incline_angle'] = False
                    
                    # Add to new path content
                    new_path_content[new_section_id] = new_section
            else:
                # Not a section, keep as is
                new_path_content[key] = value
        
        # Add the updated path to the new road data
        new_road_data[path_id] = new_path_content
    
    return new_road_data