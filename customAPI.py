from flask import Flask, request, jsonify
from generatorImages import generateImage  # Ensure this module name is correct
from flask_cors import cross_origin

app = Flask(__name__)

@app.route('/generate-image', methods=['POST'])
@cross_origin(origins='http://localhost:3000')  # Allow React app to access this route
def generate_image():
    data = request.json
    station_name = data['stationName']
    track_number = data['trackNumber']

    # Call the generateImage function that now returns the base64-encoded string directly
    base64_image = generateImage(station_name, track_number)

    print('**********************')
    print(base64_image)
    print('**********************')


    # Return the base64 string as JSON
    return jsonify({'image': base64_image})

if __name__ == '__main__':
    app.run(debug=True)
