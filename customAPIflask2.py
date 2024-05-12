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
        return jsonify({'error': 'No departures found'}), 404

    # Assuming taking the first departure for simplicity
    first_departure = departures[0]
    vehicle_id = first_departure.get('vehicle', '')

    # Fetch composition for the train
    composition_params = {
        'id': vehicle_id,
        'format': 'json',
        'lang': 'en',
        'data': 'all'
    }
    composition_response = requests.get(f'{api_base}/composition/', params=composition_params)
    composition_data = composition_response.json()

    # Parse train composition
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
            }
            for car in seg.get('units', {}).get('unit', [])
        ]
    } for seg in segments]

    response = {
        'stationName': station['name'],
        'stationID': station['id'],
        'numberOfPlatform': len(departures),
        'TrainInRailwayStation': [{
            'railwayID': first_departure['id'],
            'platformType': first_departure.get('platforminfo', {}).get('name', 'unknown'),
            'train': {
                'trainID': vehicle_id,
                'trainName': first_departure.get('vehicleinfo', {}).get('shortname', 'unknown'),
                'segments': parsed_segments,
                'direction': 'left',  # Example
                'details': 'Details not available'
            }
        }]
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
