import functionstrain as ft
import flask
import datetime

app = flask.Flask(__name__)

@app.route('/')
def accueil():
    return flask.render_template('accueil.html')

@app.route('/search', methods=['GET'])
def search():
    query = flask.request.args.get('query')
    liste_départs=[]
    for element in ft.liveBoard(query)['departures']['departure']:
        timestamp = int(element['time'])
        date = datetime.datetime.fromtimestamp(timestamp)
        heure = date.strftime('%H:%M')
        liste_départs.append(element['station']+"  "+ heure)
    return flask.render_template('gare_details.html', gare_name=query,liste_départs=liste_départs)

@app.route('/depart', methods=['GET'])
def depart():
    #getting the full name of the ride
    query=flask.request.args.get('destination')
    #getting the destination
    nom=query[0:-7]
    #getting the hour
    heure=query[-5:]+':00'
    #transforming it into timestamp
    heurebis=datetime.time(int(heure[0]+heure[1]),int(heure[3]+heure[4]),0)
    #comparing the hours to know if the travel is today or tomorrow before getting the timestamp
    if datetime.datetime.now().time()>heurebis:
        heure_complete = datetime.datetime.combine(datetime.datetime.now().date() + datetime.timedelta(days=1), datetime.datetime.strptime(heure, '%H:%M:%S').time())
        timestamp=heure_complete.timestamp()
    else:
        heure_complete = datetime.datetime.combine(datetime.datetime.now().date(), datetime.datetime.strptime(heure, '%H:%M:%S').time())
        timestamp=heure_complete.timestamp()


if __name__ == '__main__':
    app.run(debug=True)
