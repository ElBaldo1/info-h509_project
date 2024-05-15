from flask import Flask, request, jsonify
from generatorImages import generateImage  # Ensure this module name is correct
from flask_cors import cross_origin

app = Flask(__name__)

@app.route('/generate-image', methods=['POST'])
@cross_origin(origins='http://localhost:3000')  # Allow React app to access this route
def generate_image():
    data = request.json
    print('data',data)
    trackNumber =data['trackNumber']
    stationName =data['stationName']
    base64= generateImage(stationName,trackNumber)

    #print(generateImage('Brussels-North', 7))

    # Return the base64 string as JSON
    return jsonify({'image': base64})

if __name__ == '__main__':
    app.run(debug=True)
