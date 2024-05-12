from flask import Flask, jsonify, request
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/traininfo/')
def train_info():
    station_name = request.args.get('station_name')
    api_base = 'https://api.irail.be'

    # Fetch station data
    station_params = {'format': 'json', 'lang': 'en'}
    station_response = requests.get(f'{api_base}/stations/', params=station_params)
    stations = station_response.json().get('station', [])

    # Find the matching station based on the station name
    station = next((s for s in stations if station_name.lower() in s['name'].lower()), None)
    if not station:
        print("No matching station found for:", station_name)
        return jsonify({'error': 'No matching station found'}), 404

    # Fetch liveboard data for the station
    liveboard_params = {
        'id': station['id'],
        'format': 'json',
        'lang': 'en',
        'arrdep': 'departure'
    }
    liveboard_response = requests.get(f'{api_base}/liveboard/', params=liveboard_params)
    liveboard_data = liveboard_response.json()

    departures = liveboard_data.get('departures', {}).get('departure', [])
    if not departures:
        print("No departures found at station:", station['name'])
        return jsonify({'error': 'No departures found'}), 404

    trains = []
    # Process each departure separately
    for departure in departures:
        vehicle_id = departure.get('vehicle', '')

        # Fetch composition for the train
        composition_params = {
            'id': vehicle_id,
            'format': 'json',
            'lang': 'en',
            'data': 'all'
        }
        composition_response = requests.get(f'{api_base}/composition/', params=composition_params)
        print("Fetched composition for vehicle ID", vehicle_id, ":", composition_response.json())  # Log composition data
        composition_data = composition_response.json()

        if 'composition' not in composition_data or not composition_data['composition'].get('segments'):
            print("No composition or segments found for vehicle:", vehicle_id)
            continue

        segments = composition_data.get('composition', {}).get('segments', {}).get('segment', [])
        parsed_segments = [{
            'segmentID': seg['id'],
            'carriage': [
                {
                    'number': car['materialNumber'],
                    'class': 'second' if int(car.get('seatsSecondClass', 0)) > int(car.get('seatsFirstClass', 0)) else 'first',
                    'features': [
                        'bike' if int(car.get('hasBikeSection', 0)) > 0 else '',
                        'wheelchair' if int(car.get('hasPriorityPlaces', 0)) > 0 else ''
                    ]
                } for car in seg.get('units', {}).get('unit', [])
            ]
        } for seg in segments]

        print("-------------------")
        print("segments:", segments)
        print("-------------------")

        train_info = {
            'railwayID': departure['id'],
            'platformType': departure.get('platforminfo', {}).get('name', 'unknown'),
            'train': {
                'trainID': vehicle_id,
                'trainName': departure.get('vehicleinfo', {}).get('shortname', 'unknown'),
                'segments': parsed_segments,
                'direction': 'left',  # Example
                'details': 'Details not available'
            }
        }
        trains.append(train_info)



    response = {
        'stationName': station['name'],
        'stationID': station['id'],
        'numberOfPlatform': len(departures),
        'TrainInRailwayStation': trains
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
