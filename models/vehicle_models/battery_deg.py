
def route_analysis(detailed_results, current_list, consumptions, OCV, Capacity, base_k = 0.200 ,c_rate_exp = 0.2286):
    '''Take in a specific route and calculate the expected capacity loss due to degradation  through the route.
    
    Inputs
        current_list: list of current consumption through route
        consumptions: list of energy consumptions through route
        times: list of times spent along each section
        OCV: Nominal open circuit voltage
        Capacity: Original battery capacity
    Output:
        capacity_loss: expected capacity loss in Ah
    '''
    def extract_times(detailed_results):
        """        
        Args:
            detailed_results: Dictionary containing detailed route segments and their data
            
        Returns:
            list: List of time values from all path segments
        """
        time_list = [
            data["time"]
            for key, value in detailed_results.items()
            if 'path' in key
            for _, data in value.items()
        ]
        
        return time_list

    def calc_capacity_reduction(consumption):
        loss = consumption/OCV
        return loss

    def update_capacity_with_loss(current_list, consumptions, initial_capacity, OCV):
        # Initialize the capacity list with the initial capacity
        capacity_list = [initial_capacity]
        c_rates_list = []
        
        # For each step, calculate the loss and update the capacity
        for i in range(len(consumptions)):
            # Calculate capacity loss from the consumption
            loss = calc_capacity_reduction(consumptions[i])
            
            # Update the capacity by subtracting the loss
            current_capacity = capacity_list[-1] - loss
            capacity_list.append(current_capacity)
            
            # Calculate C-rate using the current capacity (not the initial one)
            c_rate = current_list[i] / current_capacity if current_capacity > 0 else float('inf')
            c_rates_list.append(c_rate)
        
        # Remove the initial capacity as it's not associated with any consumption
        capacity_list.pop(0)
        
        return capacity_list, c_rates_list


    capacity_list, c_rates_list = update_capacity_with_loss(current_list, consumptions, Capacity, OCV)
    # ----------------------------------------
    # Capacity Loss Calculation
    # ----------------------------------------
    
    def compute_capacity_loss(c_rate_list, time_list, k=base_k, n=c_rate_exp):
        """
        Computes total capacity loss based on an empirical degradation model.
        
        cap_loss = k * (C-rate ^ n) * cycle_fraction
        """
        cap_losses = []
        
        for c_rate, time in zip(c_rate_list, time_list):
            cycle_fraction = (time / 3600) * c_rate  # Convert time from seconds to cycles
            cap_loss = k * (c_rate ** n) * cycle_fraction
            cap_losses.append(cap_loss)

        return sum(cap_losses)

    # Calculate capacity loss
    cap_loss = compute_capacity_loss(c_rates_list, extract_times(detailed_results))

    return cap_loss


