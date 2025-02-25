import numpy as np


def physical_model(vehicle_data, static_data: dict, road_data):
    '''
    calculate power required to move the vehicle along specified route
    '''
    avg_incline_angle = np.radians(road_data["avg_incline_angle"])
    #Force from air resistance
    drag_force = 0.5 * static_data["air_dens"] * vehicle_data["frontal_area"] * vehicle_data["drag_coeff"] * road_data["velocity"]**2
    #Force from overcoming incline, or rolling down incline
    grav_force = vehicle_data["mass"] * static_data["grav_acc"] * np.sin(avg_incline_angle)

    #Force opposing motion due to friction
    roll_res_force = vehicle_data["mass"] * static_data["grav_acc"] * np.cos(avg_incline_angle) * vehicle_data["roll_res"]
    #force needed to overcome these resistances and move the vehicle
    tract_force = drag_force + grav_force + roll_res_force + (vehicle_data["mass"] * road_data["acceleration"])
    tract_power = max(0, tract_force * road_data["velocity"])
    return tract_power

def battery_power_model(tract_power, motor_eff):
    '''
    Takes in required power for the motor, and finds power required from the battery.
    '''
    P_batt = tract_power/motor_eff
    return P_batt

def discharge_current(OCV:float, R_i: float, P_batt: float)-> float:
    '''
    Find discharge currrent
    '''
    I_l = (OCV - (OCV**2 -4*OCV*P_batt)**0.5)/(2*R_i)
    return I_l

def find_crate(current:float, capacity : float)->float:
    '''
    Find the discharge rate from an instantaneous current value
    '''
    c_rate = current / capacity
    return c_rate


def get_edge_consumption(power: float, road_data: dict)-> float:
    '''
    Function that takes in the params from the vehicle and the edge and then calculates the route
    '''
    speed = road_data["velocity"]
    distance = road_data["distance"]
    time = distance/speed
    energy_J = time * power
    energy = energy_J/3600

    return energy
