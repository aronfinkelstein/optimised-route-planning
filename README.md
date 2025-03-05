# EAV-VRP

VRP model leveraging VRP-algorithms to optimise routes for an EV

## Project Structure

.
├── README.md
├── data_collection
│   ├── data
│   │   ├── analysed_dis_data.json
│   │   ├── discretised_data.json
│   │   ├── edge_data.csv
│   │   ├── node_data.csv
│   │   ├── random_weight_edge.csv
│   │   ├── stop_start_data.json
│   │   └── test_data.json
│   └── data_acquisition
│   ├── discretise_data.ipynb
│   ├── discretising.py
│   ├── elevation_pull.ipynb
│   ├── elevation_pull.py
│   ├── stopstart.ipynb
│   └── stopstart.py
├── main.py
├── main_test.ipynb
├── models
│   ├── road_network
│   │   ├── create_graph.py
│   │   ├── graph.py
│   │   ├── openstreetmaps.py
│   │   └── testroadnet.ipynb
│   ├── vehicle_models
│   │   ├── battery_data.json
│   │   ├── energy_consumption.py
│   │   ├── static_data.json
│   │   ├── testvehhmod.ipynb
│   │   └── vehicle_data.json
│   └── weighting
│   ├── weight_integration.py
│   └── weight_model.py
├── requirements.txt
└── simulation
----└── simulate_routes.py
