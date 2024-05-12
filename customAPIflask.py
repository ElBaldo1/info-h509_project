from flask import Flask, jsonify, request
import requests
from flask_cors import CORS
from zexin_f import getStationLocationById, fetchTrainComposition, getPlatformMarker, getSignal,getStationIdByName

app = Flask(__name__)
CORS(app)

@app.route('/api/traininfo/')
def train_info():
    station_name = request.args.get('station_name')
    api_base = 'https://api.irail.be'

    # Fetch station data
    station_params = {'format': 'json', 'lang': 'en'}
    station_response = getStationIdByName(station_name)
    stations = station_response.json().get('station', [])

    # Find the matching station based on the station name
    station = next((s for s in stations if station_name.lower() in s['name'].lower()), None)
    if not station:
        return jsonify({'error': 'No matching station found'}), 404

    station_id = station['id']
    station_location = getStationLocationById(station_id)

    # Fetch liveboard and train composition data
    liveboard_params = {
        'id': station_id,
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
    composition_data = fetchTrainComposition(vehicle_id)

    # Fetch platform markers and signals
    platform_markers = getPlatformMarker(station_id)
    signals = getSignal(station_id)

    response = {
        'stationName': station['name'],
        'stationID': station_id,
        'location': station_location,
        'numberOfPlatform': len(departures),
        'TrainInRailwayStation': [{
            'railwayID': first_departure['id'],
            'platformType': first_departure.get('platforminfo', {}).get('name', 'unknown'),
            'train': {
                'trainID': vehicle_id,
                'trainName': first_departure.get('vehicleinfo', {}).get('shortname', 'unknown'),
                'segments': composition_data,
                'direction': 'left',  # Example
                'details': 'Details not available'
            },
            'platformMarkers': platform_markers,
            'signals': signals
        }]
    }

    print('-----------------------------------')
    print(response)
    print('-----------------------------------')

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
