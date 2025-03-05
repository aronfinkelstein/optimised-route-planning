
def display_route_results(results, route_dict):
    '''
    Displays the results for a given route, based on results from ec.process_route_segments:
        results = ec.process_route_segments(
            segments, vehicle_data, static_data, 
            target_velocity, max_motor_power, motor_efficiency, 
            battery_data["OCV"], battery_data["R_internal"], 
            battery_data["Capacity"] )   
        
    
    '''
# Display results
    # Display results
    print("\nE-BIKE ENERGY CONSUMPTION SIMULATION RESULTS\n" + "="*60)
    total_energy = 0
    total_distance = 0
    total_time = 0
    max_c_rate = 0
    max_current = 0
    weighted_avg_c_rate = 0
    total_weighted_time = 0

    for i, (segment, result) in enumerate(zip(route_dict, results)):
        print(f"SEGMENT {i+1}: {segment['segment_name']}")
        print(f"  Distance: {segment['distance']:.1f} m")
        print(f"  Incline: {segment['avg_incline_angle']:.1f}°")
        print(f"  Initial velocity: {result['initial_velocity']:.2f} m/s ({result['initial_velocity']*3.6:.1f} km/h)")
        print(f"  Final velocity: {result['final_velocity']:.2f} m/s ({result['final_velocity']*3.6:.1f} km/h)")
        print(f"  Acceleration: {result['acceleration']:.3f} m/s²")
        
        # Get energy consumption and time
        if "total_energy" in result:
            energy = result["total_energy"]
            time = result["total_time"]
            
            # Get current and C-rate information
            peak_current = result["peak_discharge_current"]
            peak_c_rate = result["peak_c_rate"]
            avg_current = result["avg_discharge_current"]
            avg_c_rate = result["avg_c_rate"]
            
            print(f"  Time: {time:.2f} seconds")
            print(f"  Energy: {energy:.2f} Wh")
            print(f"  Peak Current: {peak_current:.2f} A (C-rate: {peak_c_rate:.2f}C)")
            print(f"  Avg Current: {avg_current:.2f} A (C-rate: {avg_c_rate:.2f}C)")
            
            # Show breakdown for acceleration and constant phases
            accel_phase = result["acceleration_phase"]
            const_phase = result["constant_phase"]
            print(f"    • Acceleration phase: {accel_phase['distance']:.1f}m, {accel_phase['time']:.2f}s, {accel_phase['energy']:.2f} Wh")
            print(f"      Current: {accel_phase['discharge_current']:.2f} A (C-rate: {accel_phase['c_rate']:.2f}C)")
            print(f"    • Constant phase: {const_phase['distance']:.1f}m, {const_phase['time']:.2f}s, {const_phase['energy']:.2f} Wh")
            print(f"      Current: {const_phase['discharge_current']:.2f} A (C-rate: {const_phase['c_rate']:.2f}C)")
            
            # Track maximum values
            if peak_current > max_current:
                max_current = peak_current
            if peak_c_rate > max_c_rate:
                max_c_rate = peak_c_rate
                
            # Add to weighted average calculation (only for valid time values)
            if isinstance(time, (int, float)) and time > 0:
                weighted_avg_c_rate += avg_c_rate * time
                total_weighted_time += time
        else:
            energy = result["energy_consumption"]
            time = result["time"]
            
            # For simple case, get the single current and C-rate values
            current = result.get("discharge_current", 0)
            c_rate = result.get("c_rate", 0)
            
            print(f"  Time: {time:.2f} seconds")
            print(f"  Energy: {energy:.2f} Wh")
            print(f"  Current: {current:.2f} A (C-rate: {c_rate:.2f}C)")
            
            # Track maximum values
            if current > max_current:
                max_current = current
            if c_rate > max_c_rate:
                max_c_rate = c_rate
                
            # Add to weighted average calculation (only for valid time values)
            if isinstance(time, (int, float)) and time > 0:
                weighted_avg_c_rate += c_rate * time
                total_weighted_time += time
        
        print(f"  Target speed reached: {'Yes' if result['reached_target'] else 'No'}")
        print("")
        
        total_energy += energy
        total_distance += segment['distance']
        total_time += time if isinstance(time, (int, float)) else 0

    # Calculate route-wide weighted average C-rate
    if total_weighted_time > 0:
        weighted_avg_c_rate = weighted_avg_c_rate / total_weighted_time

    print("="*60)
    print(f"TOTAL ROUTE SUMMARY:")
    print(f"  Total distance: {total_distance:.1f} m")
    print(f"  Total time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
    print(f"  Total energy consumption: {total_energy:.2f} Wh")
    print(f"  Energy consumption per km: {total_energy/(total_distance/1000):.2f} Wh/km")
    print(f"  Maximum discharge current: {max_current:.2f} A")
    print(f"  Maximum C-rate: {max_c_rate:.2f}C")
    print(f"  Weighted average C-rate: {weighted_avg_c_rate:.2f}C")
    print("="*60)