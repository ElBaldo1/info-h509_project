# info-h509_project

Project for the INFO-H509 course - Geo-spatial and web technologies, in which a real-time image of a train arriving at a station is to be developed and illustrated. The aim is to show which carriages are accessible, where the first and second class carriages are located, and where the special carriages (such as those with bicycle storage) are positioned.

## Overview

This project leverages iRail APIs and OpenStreetMap (OSM) data to retrieve information about train stations, train departures (live boards), and train compositions. It also identifies railway infrastructure elements (e.g., platform markers, signals) around a given station, thereby assisting in visualizing the precise location and composition of trains on specific tracks.

## Key Features

1. **Station Information:**  
   - Fetch a list of Belgian railway stations with details such as ID, name, and coordinates.

2. **Live Board (Real-time Departures):**  
   - Retrieve upcoming departures for a station, including delays, platforms, and train IDs.

3. **Train Details & Composition:**  
   - Get detailed route information for a specific train, including all its stops.
   - Fetch the train’s composition, including which units or carriages form the train.
   - Identify the positioning of first/second class carriages and special features like bicycle compartments.

4. **Station-Track Queries:**  
   - Given a station and a track number, determine the next departing train.
   - Fetch platform markers and signals on the selected track segment.

5. **OSM Infrastructure Data:**  
   - Use OSMPythonTools and Overpass API to find platform markers and signals within a station’s vicinity.
   - Determine if these elements are within a certain boundary to ensure accurate geo-located information.

## Dependencies

- **Python 3.7+**
- **Libraries:**
  - `requests` for HTTP requests.
  - `shapely` for geometric operations.
  - `OSMPythonTools` to query OSM/Overpass data.
  - Built-in libraries: `datetime`, `json`, `argparse`, `configparser`, `copy`, `sys`, `time`
  
  Install dependencies with:
  ```bash
  pip install -r requirements.txt
 ``


## Usage Examples

### Fetch and print the next train on track 9 at Brussels-North:
```python
station_id = getStationIdByName('Bruxelles-Nord')
next_train = getNextTrainByTrack(station_id, 9)
print(next_train)
```
### Retrieve platform markers and signals for track 9 at Brussels-North:

```python
filteredPMs, filteredSignals = getPMarkerSignalByTrack('BE.NMBS.008812005', 9, rad=0.015)
for pm in filteredPMs:
    print(pm.id(), pm.tags())
for signal in filteredSignals:
    print(signal.tags())
```
## Project Files

### `main.py`  
Contains the core logic for:  
- Fetching station information, live board data, train info, and train composition.  
- Retrieving OSM platform markers and signals.  
- Filtering elements by track number and spatial boundaries.

### `utils.py`  
Contains helper functions such as:  
- Sleep timing utilities.  
- Messaging functions (if integrated).  
- Other modular utilities to support the main logic.  

## Notes
Station IDs such as BE.NMBS.008812005 are specific identifiers used in the iRail API. Use the fetchStations() function to retrieve all stations or getStationIdByName() to find a station’s ID by name.
OSM Data Retrieval: The Overpass API is used to fetch OSM elements. Be mindful of API rate limits, as excessive requests may lead to delays or blocked access.
For real-time positioning and detailed carriage visualization, additional logic (e.g., data caching, client UI integration) may be required.


