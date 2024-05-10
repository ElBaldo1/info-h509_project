from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

@app.route('/api/traininfo/')
def train_info():
    station_name = request.args.get('station_name')
    api_base = 'https://api.irail.be'

    # Fetching station data
    station_params = {
        'format': 'json',
        'lang': 'en'
    }
    station_response = requests.get(f'{api_base}/stations/', params=station_params)
    stations = station_response.json().get('station', [])

    # Finding the station ID based on station name
    station_info = next((station for station in stations if station['name'].lower() == station_name.lower()), None)
    if not station_info:
        return jsonify({'error': 'Station not found'}), 404

    # Fetching liveboard data
    liveboard_params = {
        'station': station_info['id'],
        'format': 'json',
        'lang': 'en'
    }
    liveboard_response = requests.get(f'{api_base}/liveboard/', params=liveboard_params)
    liveboard_data = liveboard_response.json()

    # Optionally fetch train composition, here taking the first train as example
    first_departure = liveboard_data.get('departures', {}).get('departure', [{}])[0]
    train_id = first_departure.get('vehicle', '')

    composition_params = {
        'id': train_id,
        'format': 'json',
        'lang': 'en',
        'data': 'all'
    }
    composition_response = requests.get(f'{api_base}/composition/', params=composition_params)
    composition_data = composition_response.json()

    # Compiling the result
    result = {
        'stationName': station_info['name'],
        'stationID': station_info['id'],
        'liveboard': liveboard_data.get('departures', {}),
        'trainComposition': composition_data.get('composition', {}) if train_id else None
    }

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
