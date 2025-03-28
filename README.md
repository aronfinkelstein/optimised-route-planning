<a id="readme-top"></a>
<br />

<div align="center">
  <a href="images/sat_map.jpg">
    <img src="images/sat_map.jpg" alt="Logo" width="800">
  </a>

  <h3 align="center">Optimised Route-Planning</h3>

  <p align="center">
    Modelling the impacts of an optimised route-planning algorithm on battery health and energy consumption for an EV
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About The Project

<div align="center">
  <a href="images/systemdiagram.jpg">
    <img src="images/systemdiagram.jpg" alt="Logo" width="800">
  </a>
</div>

This project was used to model the impact of an optimised route-planning algorithm on battery health and energy consumption for an eCargo bike. All simulations were ran using code in this repository. This version has the essential models to run simulations, with notebooks used to run the overall end of life simulations and validation studies. The overall system can be seen in the image above. This image shows:

- A road network model: built using OSM and Google Maps API data, compiled into a connected graph using Networkx.
- Dijkstra's Algorithm: shortest-path algorithm implemented with networkx and influenced by weight calculations made within this project.
- Consumption Model: model that takes road and vehicle characteristics as an input, and outputs energy demands.
- Ageing Model : model used to predict the degradation (in terms of capacity loss) of the EV battery using Peukert's relationship.

## Getting Started

To get a local copy up and running follow these simple example steps.

### Installation

1. Get a Google Maps Elevation API Key at [Google Cloud Platform](https://cloud.google.com/maps-platform/)
2. Clone the repo

   ```sh
   git clone https://github.com/github_username/repo_name.git
   ```

3. Install python packages
   ```sh
   pip install -r requirements.txt
   ```
4. Create a .env file in the project root and add your API key
   ```sh
   GOOGLE_API="YOUR_GOOGLE_MAPS_API_KEY"
   ```
5. Change git remote url to avoid accidental pushes to base project
   ```sh
   git remote set-url origin github_username/repo_name
   git remote -v # confirm the changes
   ```
   <p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

### Simulate Routes

The main.py file is set up to simulate and analyse a random route from the network. Run this file to visualise a random route and see the consumption, distance, and climb for a given route.

### Adapt to different network

Inside 'data_collection/data_acquisition', find scripts used to pull, process, and store the data for a given map. Set a different central point, with a different radius if needed, to process and download necessary data.

```python
central_point = (51.456127, -2.608071) #latitude, longitude
G = ox.graph_from_point(central_point, dist=500, network_type='bike')
```

### Optimise Weight Calculation

The optimise-weights.ipnyb notebook was used to optimise weights, using parallelised simulations. These resulting weights are stored in the weights.json inside the data_collection directory. If needed, re-run the ipnyb notebook and replace these weights with the new weights calculated.

### Change vehicle data

Inside the models/vehicle_models directory are three json files with data used to model the specific vehicle for this project. Change this data to model a different vehicle.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Key Resources

Use this space to list resources you find helpful and would like to give credit to. I've included a few of my favorites to kick things off!

- [Open Street Maps (OSM)](https://www.openstreetmap.org/)
- [OSMnx Documentation](https://osmnx.readthedocs.io)
- [Networkx Documentation](https://networkx.org/)
- [Google Maps Elevation API](https://developers.google.com/maps/documentation/elevation/start)
<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contact

Aron Finkelstein - finkelstein.aron@gmail.com

<p align="right">(<a href="#readme-top">back to top</a>)</p>
