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
    I_l = (OCV - (OCV**2 - 4*R_i*P_batt)**0.5) / (2*R_i)
    return I_l

def find_crate(current:float, capacity : float)->float:
    '''
    Find the discharge rate from an instantaneous current value
    '''
    c_rate = current / capacity
    return c_rate


def get_edge_consumption(power: float, road_data: dict) -> float:
    '''
    Function that takes in the params from the vehicle and the edge and then calculates the route
    
    Fixed to handle zero velocity cases safely
    '''
    speed = road_data["velocity"]
    distance = road_data["distance"]
    
    # Handle zero velocity case
    if speed <= 0:
        return 0  # No energy consumption if not moving
    
    time = distance / speed
    energy_J = time * power
    energy = energy_J / 3600  # Convert to Wh

    return energy

def calculate_required_acceleration(v_initial, v_final, distance):
    """
    Calculate the required acceleration to reach target speed within the given distance.
    
    Parameters:
    v_initial (float): Initial velocity in m/s
    v_final (float): Target velocity in m/s
    distance (float): Available distance in meters
    
    Returns:
    float: Required acceleration in m/s²
    """
    return (v_final**2 - v_initial**2) / (2 * distance)

def calculate_max_available_acceleration(vehicle_data, static_data, road_data, max_motor_power):
    """
    Calculate the maximum possible acceleration given power constraints and hill grade.
    
    Parameters:
    vehicle_data (dict): Vehicle characteristics (mass, drag coefficient, etc.)
    static_data (dict): Static values like gravity, air density
    road_data (dict): Road segment data including incline, velocity
    max_motor_power (float): Maximum power available from the motor in Watts
    
    Returns:
    float: Maximum possible acceleration in m/s²
    """
    # Calculate forces at current speed without acceleration component
    avg_incline_angle = np.radians(road_data["avg_incline_angle"])
    
    # Force from air resistance
    drag_force = 0.5 * static_data["air_dens"] * vehicle_data["frontal_area"] * vehicle_data["drag_coeff"] * road_data["velocity"]**2
    
    # Force from overcoming incline
    grav_force = vehicle_data["mass"] * static_data["grav_acc"] * np.sin(avg_incline_angle)
    
    # Force opposing motion due to friction
    roll_res_force = vehicle_data["mass"] * static_data["grav_acc"] * np.cos(avg_incline_angle) * vehicle_data["roll_res"]
    
    # Total force needed to maintain current speed
    maintain_force = drag_force + grav_force + roll_res_force
    
    # Power needed to maintain current speed
    maintain_power = maintain_force * road_data["velocity"]
    
    # Available power for acceleration
    available_power = max(0, max_motor_power - maintain_power)
    
    # Max acceleration possible with available power
    # F = m*a, P = F*v, therefore a = P/(m*v)
    if road_data["velocity"] > 0:
        max_acceleration = available_power / (vehicle_data["mass"] * road_data["velocity"])
    else:
        # If starting from standstill, use a small non-zero velocity to avoid division by zero
        max_acceleration = available_power / (vehicle_data["mass"] * 0.1)
    
    return max_acceleration

def calculate_actual_acceleration(v_initial, v_final, distance, vehicle_data, static_data, road_data, max_motor_power):
    """
    Calculate the actual acceleration considering both required acceleration and power limitations.
    
    Parameters:
    v_initial (float): Initial velocity in m/s
    v_final (float): Target velocity in m/s
    distance (float): Available distance in meters
    vehicle_data (dict): Vehicle characteristics
    static_data (dict): Static values
    road_data (dict): Road segment data
    max_motor_power (float): Maximum motor power in Watts
    
    Returns:
    tuple: (actual_acceleration, will_reach_target, adjusted_final_velocity)
    """
    required_accel = calculate_required_acceleration(v_initial, v_final, distance)
    
    # For accurate max acceleration calculation, we need to use average velocity during acceleration
    avg_velocity = (v_initial + v_final) / 2
    temp_road_data = road_data.copy()
    temp_road_data["velocity"] = avg_velocity
    
    max_available_accel = calculate_max_available_acceleration(
        vehicle_data, static_data, temp_road_data, max_motor_power
    )
    
    if required_accel <= max_available_accel:
        # We can reach the target speed
        return required_accel, True, v_final
    else:
        # Can't reach target speed in the given distance with available power
        # Calculate what speed we can reach
        adjusted_v_final = np.sqrt(v_initial**2 + 2 * max_available_accel * distance)
        return max_available_accel, False, adjusted_v_final

def calculate_segment_energy_with_acceleration(v_initial, v_target, segment_data, vehicle_data, static_data, max_motor_power, motor_efficiency):
    """
    Calculate energy consumption for a segment considering acceleration phase.
    
    Fixed to handle zero velocity cases safely
    
    Parameters:
    v_initial (float): Initial velocity in m/s
    v_target (float): Target velocity in m/s
    segment_data (dict): Segment data including distance, incline, etc.
    vehicle_data (dict): Vehicle characteristics
    static_data (dict): Static values
    max_motor_power (float): Maximum motor power in Watts
    motor_efficiency (float): Motor efficiency (0-1)
    
    Returns:
    dict: Energy consumption details
    """
    distance = segment_data["distance"]
    
    # Calculate actual acceleration and final velocity
    accel, will_reach_target, v_final = calculate_actual_acceleration(
        v_initial, v_target, distance, vehicle_data, static_data, segment_data, max_motor_power
    )
    
    # Handle negative or zero acceleration (e.g., very steep hill)
    if accel <= 0:
        # If we can't accelerate (very steep hill), use constant speed model
        segment_data_copy = segment_data.copy()
        segment_data_copy["acceleration"] = 0
        
        # If initial velocity is 0, we can't move on this segment
        if v_initial <= 0:
            return {
                "initial_velocity": 0,
                "final_velocity": 0,
                "acceleration": 0,
                "time": float('inf'),  # Can't complete the segment
                "energy_consumption": 0,  # No energy used if not moving
                "reached_target": False
            }
        
        segment_data_copy["velocity"] = v_initial
        tract_power = physical_model(vehicle_data, static_data, segment_data_copy)
        batt_power = battery_power_model(tract_power, motor_efficiency)
        time = distance / v_initial
        energy = batt_power * time / 3600  # Convert to Wh
        
        return {
            "initial_velocity": v_initial,
            "final_velocity": v_initial,
            "acceleration": 0,
            "time": time,
            "energy_consumption": energy,
            "reached_target": False
        }
    
    # Calculate time needed for acceleration
    accel_time = (v_final - v_initial) / accel
    
    # Calculate distance covered during acceleration
    accel_distance = v_initial * accel_time + 0.5 * accel * accel_time**2
    
    # Check if we use the entire segment for acceleration
    if accel_distance >= distance:
        # We're still accelerating at the end of the segment
        # Recalculate time and final velocity for the given distance
        # v_final² = v_initial² + 2*a*d
        adjusted_v_final = np.sqrt(v_initial**2 + 2 * accel * distance)
        accel_time = (adjusted_v_final - v_initial) / accel if accel > 0 else 0
        
        # Calculate average velocity during acceleration
        avg_velocity = (v_initial + adjusted_v_final) / 2
        
        # Set up data for energy calculation
        segment_data_accel = segment_data.copy()
        segment_data_accel["velocity"] = max(0.1, avg_velocity)  # Ensure non-zero velocity
        segment_data_accel["acceleration"] = accel
        
        # Calculate power and energy for acceleration phase
        tract_power_accel = physical_model(vehicle_data, static_data, segment_data_accel)
        batt_power_accel = battery_power_model(tract_power_accel, motor_efficiency)
        energy_accel = batt_power_accel * accel_time / 3600  # Convert to Wh
        
        return {
            "initial_velocity": v_initial,
            "final_velocity": adjusted_v_final,
            "acceleration": accel,
            "time": accel_time,
            "energy_consumption": energy_accel,
            "reached_target": adjusted_v_final >= v_target
        }
    else:
        # We reach the target/max velocity before the end of the segment
        # Calculate energy for acceleration phase
        avg_velocity_accel = (v_initial + v_final) / 2
        segment_data_accel = segment_data.copy()
        segment_data_accel["velocity"] = max(0.1, avg_velocity_accel)  # Ensure non-zero velocity
        segment_data_accel["acceleration"] = accel
        segment_data_accel["distance"] = accel_distance
        
        tract_power_accel = physical_model(vehicle_data, static_data, segment_data_accel)
        batt_power_accel = battery_power_model(tract_power_accel, motor_efficiency)
        energy_accel = batt_power_accel * accel_time / 3600  # Convert to Wh
        
        # Calculate energy for constant velocity phase
        constant_distance = distance - accel_distance
        constant_time = constant_distance / v_final if v_final > 0 else 0
        
        segment_data_const = segment_data.copy()
        segment_data_const["velocity"] = v_final
        segment_data_const["acceleration"] = 0
        segment_data_const["distance"] = constant_distance
        
        tract_power_const = physical_model(vehicle_data, static_data, segment_data_const)
        batt_power_const = battery_power_model(tract_power_const, motor_efficiency)
        energy_const = batt_power_const * constant_time / 3600  # Convert to Wh
        
        total_time = accel_time + constant_time
        total_energy = energy_accel + energy_const
        
        return {
            "initial_velocity": v_initial,
            "final_velocity": v_final,
            "acceleration": accel,
            "acceleration_phase": {
                "distance": accel_distance,
                "time": accel_time,
                "energy": energy_accel
            },
            "constant_phase": {
                "distance": constant_distance,
                "time": constant_time,
                "energy": energy_const
            },
            "total_time": total_time,
            "total_energy": total_energy,
            "reached_target": will_reach_target
        }

# Example usage:
def process_route_segments(segments, vehicle_data, static_data, target_velocity, max_motor_power, motor_efficiency):
    """
    Process a sequence of route segments and calculate energy consumption.
    """
    current_velocity = 0  # Start from standstill
    results = []
    
    for segment in segments:
        # Reset velocity to 0 if:
        # 1. It's explicitly marked as a stop_start segment OR
        # 2. The segment is marked as the start of an "unsmooth" path
        if segment.get("stop_start", False) or segment.get("unsmooth_start", False):
            current_velocity = 0
        
        # Calculate energy consumption for this segment
        segment_result = calculate_segment_energy_with_acceleration(
            current_velocity, target_velocity, segment, 
            vehicle_data, static_data, max_motor_power, motor_efficiency
        )
        
        # Update current velocity for next segment
        current_velocity = segment_result["final_velocity"]
        
        results.append(segment_result)
    
    return results


# This assumes your original functions are available:
# physical_model, battery_power_model, get_edge_consumption