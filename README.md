# EAV-VRP

VRP model leveraging VRP-algorithms to optimise routes for an EV

## Project Structure

```
.
├── README.md
├── analysis
│   ├── analyse_route.ipynb
│   └── analyse_route.py
├── config.py
├── data_collection
│   ├── data
│   │   ├── large_net
│   │   └── small_net
│   └── data_acquisition
│       ├── correct_climbs_angles.ipynb
│       ├── discretise_data.ipynb
│       ├── discretising.py
│       ├── elevation_pull.ipynb
│       ├── elevation_pull.py
│       ├── large_net_assembley.ipynb
│       ├── stopstart.ipynb
│       └── stopstart.py
├── main.py
├── main_test.ipynb
├── models
│   ├── road_network
│   │   ├── __init__.py
│   │   ├── cache
│   │   ├── create_graph.py
│   │   ├── graph.py
│   │   ├── openstreetmaps.py
│   │   └── testroadnet.ipynb
│   ├── vehicle_models
│   │   ├── battery_data.json
│   │   ├── battery_deg.py
│   │   ├── debug_consumption_model.ipynb
│   │   ├── energy_consumption.py
│   │   ├── static_data.json
│   │   ├── testvehhmod.ipynb
│   │   └── vehicle_data.json
│   └── weighting
│       ├── weight_integration.py
│       └── weight_model.py
├── optimization_logs
│   ├── opt_run_20250311_142320
│   ├── opt_run_20250311_143447
│   ├── opt_run_20250311_163242
│   └── opt_run_20250311_171317
├── parallel_test.ipynb
├── parameter_exploration_compact.png
├── requirements.txt
├── simresults.txt
├── simulation
│   ├── display_results.py
│   ├── simulate_routes.py
│   └── test_simulation.ipynb
├── test_data
│   ├── test_input_route.json
│   └── test_output.json
└── weights_test.ipynb
```
