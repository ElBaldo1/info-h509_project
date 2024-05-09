import requests

# Base URL for the iRail API
baseUrl = "https://api.irail.be/"

# Endpoint for the liveboard information
url = baseUrl + "liveboard/"
params = {
    "id": "BE.NMBS.008892007",  # Station ID for Gent-Sint-Pieters
    "station": "Gent-Sint-Pieters",
    "date": "300917",  # Date in the format ddmmyy
    "time": "1230",    # Time in the format HHmm
    "arrdep": "departure",  # Fetching information for departures
    "lang": "en",      # Response language set to English
    "format": "json",  # Response format set to JSON
    "alerts": "false"  # Do not include alerts in the response
}

try:
    # Perform the API request
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        print(data)
    else:
        print("Failed to retrieve data. Status code:", response.status_code)
except requests.exceptions.RequestException as e:
    # Handle any errors that occur during the HTTP request
    print("An error occurred:", e)

