from flask import request, render_template
import requests
from project import app


@app.route('/', methods=['GET'])
def home():
    data = driver_standing()
    return render_template('home.html', data=data), 200

def driver_standing():
    standings = requests.get('http://ergast.com/api/f1/2016/driverStandings.json')
    return standings.json()
