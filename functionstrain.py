import sys
import json, time, configparser, argparse, copy, requests
from threading import Thread
from datetime import datetime, timedelta
from datetime import datetime
from urllib import parse
#import geopandas as gpd
from shapely.geometry import Point
#See https://github.com/mocnik-science/osm-python-tools
from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.overpass import overpassQueryBuilder, Overpass
from shapely.geometry import Point, Polygon

#########################################################
#a function to get all the station info in jason format
#return a json response
#########################################################
def fetchStations():
    url = "https://api.irail.be/stations/?format=json&lang=en"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    resp = requests.request('GET', url, headers=headers).json()
    return resp

#########################################################
#a function to get the current time live board info of a station
#@param station: the name or id of the station
#return a json response
#########################################################
def liveBoard(station):
    formatted_date = datetime.now().strftime("%d%m%y")
    formatted_time = datetime.now().strftime("%H%M")
    url = f"https://api.irail.be/liveboard/?station={station}&date={formatted_date}&time={formatted_time}&arrdep=departure&lang=en&format=json&alerts=true"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    resp = requests.request('GET', url, headers=headers).json()
    return resp

#########################################################
#a function to get the info of a specific train, including the stops
#@param trainId: the id of the train
#return a json response
#########################################################
def fetchTrainInfo(trainId):
    formatted_date = datetime.now().strftime("%d%m%y")
    formatted_time = datetime.now().strftime("%H%M")
    url = f"https://api.irail.be/vehicle/?id={trainId}&date={formatted_date}&format=json&lang=en&alerts=false"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    resp = requests.request('GET', url, headers=headers).json()
    return resp

#########################################################
#a function to get the composition info of a specific train
#@param trainId: the id of the train
#return a json response
#########################################################
def fetchTrainComposition(trainId):
    url = f"https://api.irail.be/composition/?format=json&id={trainId}&data=all&lang=en"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    resp = requests.request('GET', url, headers=headers).json()
    return resp

#########################################################
#a function to get the station id from the name of the station
#@param trainName: the name of the station
#return the station id
#########################################################
def getStationIdByName(trainName):
    stations = fetchStations()
    for station in stations['station']:
        #print(station)
        #print(station['name'])
        if trainName in station['name']:
            return station['id']

#########################################################
#a function to get the stops of a specific train after a specific stop
#@param currentTrainStationId: the id of the train station after which you want to query the stops
#@param trainId: the id of the train
#return the station info after a sepcific train station
#########################################################
def getStationAfter(currentTrainStationId, trainId):
    stationAfter = []
    trainInfo = fetchTrainInfo(trainId)
    for i, stop in enumerate(trainInfo['stops']['stop']):
        #print(i, stop)
        #print(stop)
        #print(station['name'])
        if currentTrainStationId in stop['stationinfo']['id']:
            return [s['stationinfo'] for s in trainInfo['stops']['stop'][i+1:]]
        
#########################################################
#a function to get the station's latitude, longitude by station id
#@param stationId: the id of the station
#return (latitude, longitude) tuple
#########################################################
def getStationLocationById(stationId):
    stations = fetchStations()
    for station in stations['station']:
        if stationId in station['id']:
            return (float(station['locationY']), float(station['locationX']))

#########################################################
#a function to calculate haversine distance  
#@param lat1: the latitude of 1st point
#@param lon1: the longitude of 1st point
#@param lat2: the latitude of 2nd point
#@param lon2: the longitude of 2nd point
#return a haversine distance in meters. 
#########################################################
def havDistance(lat1, lon1, lat2, lon2):
    "return haversine((lat1, lon1), (lat2, lon2), unit=Unit.METERS)"

#########################################################
#a function to check if some point is in a boudry, used to find all the platform makers, signals within
#a specific station
#@param lat: the latitude of the center point
#@param lon: the longitude of the center point
#@param pointList: the list of the points in tuple, like [(x,y),(u,v),...]
#@param rad: the distance between the boundry and the center point 
#########################################################
def inBoundaryCheck(lat, lon, pointList, rad=0.02):
    # initiate a polygon with given vertices
    boundary_points = [(lat - rad, lon - rad),
                       (lat + rad, lon - rad),
                       (lat + rad, lon + rad),
                       (lat - rad, lon + rad)]
    #print('boundary_points', boundary_points)
    boundary_polygon = Polygon(boundary_points)
    #print('boundary_polygon', boundary_polygon)
    pointList = [Point(x, y) for x, y in pointList]
    #print('pointList', pointList)

    # check if in boundary
    boundaryCheck = [boundary_polygon.contains(point) for point in pointList]

    return boundaryCheck

#########################################################
#a function to get all the requested type of overpass elements (platform-markers, signals, ...) by using 
#openstreetmap APIs. the openstreetmap api is wrapped by a library called "OSMPythonTools"
#install OSMPythonTools: pip install OSMPythonTools
#@param elementType: the kind of elements you want to get, such as "platform_marker", "signal"
#return a list of elements
#########################################################
def getOSMElement(elementType):
    nominatim = Nominatim()
    areaId = nominatim.query('Belgium').areaId()
    overpass = Overpass()
    query = overpassQueryBuilder(area=areaId, elementType='nwr', selector=f'"railway"="{elementType}"', includeGeometry=True)
    result = overpass.query(query)
    elements = result.elements()
    return elements

#########################################################
#a function to get all platform markers in a station
#@param stationId: the id of the station
#return a list of OSM elements
#########################################################
def getPlatformMarker(stationId, rad=0.02):
    stationLocation = getStationLocationById(stationId)
    elements = getOSMElement('platform_marker')
    elemLocation = [(e.lat(), e.lon()) for e in elements]
    points = inBoundaryCheck(stationLocation[0], stationLocation[1], elemLocation, rad=rad)
    elemPMarker = [elements[i] for i in range(len(points)) if points[i]]
    return elemPMarker

#########################################################
#a function to get all signals in a station
#@param stationId: the id of the station
#return a list of OSM elements
#########################################################
def getSignal(stationId, rad=0.02):
    stationLocation = getStationLocationById(stationId)
    elements = getOSMElement('signal')
    elemLocation = [(e.lat(), e.lon()) for e in elements]
    points = inBoundaryCheck(stationLocation[0], stationLocation[1], elemLocation, rad=rad)
    elemPMarker = [elements[i] for i in range(len(points)) if points[i]]
    return elemPMarker

#resp_lb = liveBoard('Bruxelles-Nord')
#resp_ti = fetchTrainInfo('IC2521')
resp_tc = fetchTrainComposition('IC1832')
#print(resp_tc['composition']['segments']['segment'][0]['composition']['units']['unit'])
#stationId = getStationIdByName('Brussels-North')
#stationAfter = getStationAfter(stationId, 'IC2121')
#########################################################
#a function to get platform marker and signals of a track in a station
#@param stationId: the id of the station
#@param trackNumber: the number of track
#@param rad: the distance between the boundry and the center point
#return filteredPMs and filteredSignals of a track
#########################################################
def getPMarkerSignalByTrack(stationId, trackNumber, rad=0.015):
    pms = getPlatformMarker(stationId, rad=rad)
    signals = getSignal(stationId, rad=rad)
    filteredPMs = []
    filteredSignals = []
    for pm in pms:
        if 'ref:track' in pm.tags().keys() and pm.tags()['ref:track']==str(trackNumber):
            filteredPMs.append(pm)
    for signal in signals:
        if 'ref:track' in signal.tags().keys() and signal.tags()['ref:track']==str(trackNumber):
            filteredSignals.append(signal)
            
    return filteredPMs, filteredSignals


#########################################################
#a function to get the next train info of a track
#@param stationId: the id of the station
#@param trackNumber: the number of track
#return the next train info of a track
#########################################################
def getNextTrainByTrack(stationId, trackNumber):
    departures = liveBoard(stationId)['departures']['departure']
    departure = None
    for dptr in departures:
        if dptr['platform'] == str(trackNumber):
            departure = dptr
            break
    return departure