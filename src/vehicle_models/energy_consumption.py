import numpy as np

def process_data(edge_data)-> list:
    '''
    Function that takes in an edge and uses the data to process values and send them into the consumption model.
    '''
    pass


def physical_model(data):
    '''
    calculate power required to move the vehicle along specified route
    '''
    static_data = data["static_data"]
    vehicle_data = data["vehicle_data"]
    road_data = data["road_data"]

    #Force from air resistance
    drag_force = 0.5 * static_data["air_dens"] * vehicle_data["frontal_area"] * vehicle_data["drag_coeff"] * road_data["velocity"]**2

    #Force from overcoming incline, or rolling down incline
    grav_force = vehicle_data["mass"] * static_data["grav_acc"] * np.sin(road_data["incline_angle"])

    #Force opposing motion due to friction
    roll_res_force = vehicle_data["mass"] * static_data["grav_acc"] * np.cos(road_data["incline_angle"]) * vehicle_data["roll_res"]

    #force needed to overcome these resistances and move the vehicle
    tract_force = drag_force + grav_force + roll_res_force + (vehicle_data["mass"] * road_data["acceleration"])

    tract_power = tract_force * road_data["velocity"]

    return tract_power

def battery_model(data):
    tract_power = physical_model(data)
    vehicle_params = data["vehicle_data"]
    OCV = vehicle_params["OCV"]  # Open circuit voltage
    R1_t = vehicle_params["R1_t"]  # Resistance 1
    R2_t = vehicle_params["R2_t"]  # Resistance 2
    Ri = vehicle_params["Ri"]  # Internal resistance
    ns = vehicle_params["ns"]  # Number of series cells
    np = vehicle_params["np"]  # Number of parallel cells
    eta_em = vehicle_params["eta_em"]  # Motor efficiency
    eta_pe = vehicle_params["eta_pe"]  # Power electronics efficiency


    denominator = (OCV) * ns * np

    I_t = tract_power / denominator * (eta_em * eta_pe) ** np.sign(tract_power)

    return I_t






def get_edge_consumption(params: dict)-> float:
    '''
    Function that takes in the params from the vehicle and the edge and then calculates the route
    '''
    pass

