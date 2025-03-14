import json
from pprint import pprint
print("packages imported")

with open("../data_collection/data/large_net/fixed_large_dis_data.json", "r") as file:
    map_data = json.load(file)

def calculate_path_totals(path_data):
    total_climb = 0
    total_distance = 0
    coordinates = []

    # Iterate through each section in the data
    for key in path_data:
        # Check if the key starts with "section" to ensure we're only processing section data
        if isinstance(key, str) and key.startswith("section"):
            section = path_data[key]
            total_climb += section['climb']
            total_distance += section['distance']
            coordinates.append(section['coords'])
    
    return total_climb, total_distance, coordinates

test_set = [
    "path1897", 
    "path203", 
    "path2756", 
    "path45", 
    "path3109", 
    "path782", 
    "path1432", 
    "path67", 
    "path2314", 
    "path501"
]

def main():
    for path in test_set:
        print(f'=========={path}==========')
        data = map_data[path]
        print(f'nodes:{data['nodes']}')
        total_climb, total_distance, coordinates = calculate_path_totals(data)
        print(f'start and end coords: {coordinates[0][1],coordinates[0][0], coordinates[-1][-1], coordinates[-1][-2]}')
        print(f'distancs: {total_distance}')
        print(f'distancs: {total_climb}')

if __name__ == "__main__":
    main()