import requests
import os
import math
from geopy.distance import geodesic
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API")


def pre_process_path(path : str) -> dict:
    '''
    Takes linestring from OSM and returns dictionary of coordinates on path
    '''
    path = path.removeprefix("LINESTRING (").removesuffix(")")
    coords = path.split(", ")
    path_data = {}
    # Loop through and create dictionary entries
    for i, coord in enumerate(coords, start=1):
        lon, lat = map(float, coord.split())  # Convert to float
        path_data[f"point{i}"] = [lon, lat]
    return path_data

def find_elevation(lat: float, lon: float) -> float:
    '''
    Finds the elevation of each coordinate on the route
    '''
    url = f"https://maps.googleapis.com/maps/api/elevation/json?locations={lon},{lat}&key={API_KEY}"

    response = requests.get(url)
    data = response.json()

    if "results" in data and len(data["results"]) > 0:
        elevation = data["results"][0]["elevation"]
    return elevation

def find_euc_dist(point1: list, point2 : list) -> float:
    distance = geodesic(point1, point2).meters
    return distance

def find_climb(point1: list, point2 : list) -> float:
    '''
    Finds the climb between two points
    '''
    x1, y1 = point1
    x2, y2 = point2
    point1_el = find_elevation(x1,y1)
    point2_el = find_elevation(x2,y2)

    climb = point2_el - point1_el
    return climb

def find_incline_angle(distance: float, climb: float):
    if distance == 0:
        return 0 
    angle_rad = math.atan(climb / distance)
    angle_deg = math.degrees(angle_rad)
    return round(angle_deg,2)


def assemble_path_data(path: str) -> dict:
    '''
    returns a dict of information from an individual path from the csv
    '''
    #initialise dicts
    pathway = pre_process_path(path)
    sections = {}

    keys = list(pathway.keys())
    for i in range(len(keys) - 1):
        section_name = f"section{i+1}"
        coords1 = pathway[keys[i]]
        coords2 = pathway[keys[i+1]]
        climb = find_climb(coords1, coords2)
        dist = find_euc_dist(coords1, coords2)
        angle = find_incline_angle(dist, climb)

        sections[section_name] = {
            "points": [keys[i], keys[i+1]],
            "coords": coords1 + coords2,
            "climb" : climb,
            "distance" : dist,
            "avg_incline_angle" : angle
        }

    return sections    

