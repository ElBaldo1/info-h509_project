import functionstrain as ft
import flask
import datetime

app = flask.Flask(__name__)

@app.route('/')
def accueil():
    return flask.render_template('accueil.html')

@app.route('/search', methods=['GET'])
def search():
    query = flask.request.args.get('query')  # Récupère la requête de l'utilisateur depuis l'URL
    liste_départs=[]
    for element in ft.liveBoard(query)['departures']['departure']:
        timestamp = int(element['time'])
        date = datetime.datetime.fromtimestamp(timestamp)
        heure = date.strftime('%H:%M')
        liste_départs.append(element['station']+"  "+ heure)
    return flask.render_template('gare_details.html', gare_name=query,liste_départs=liste_départs)

if __name__ == '__main__':
    app.run(debug=True)
