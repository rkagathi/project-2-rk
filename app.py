# Flask and database setup
import pandas as pd
import requests
from flask import (
    Flask,
    render_template,
    request, 
    redirect,
    jsonify)
from flask_sqlalchemy import SQLAlchemy
from aqi2json import aqi2json
import pymongo

# Flask Setup
app = Flask(__name__)

# Database Setup
# The database URI
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db/aqi.sqlite"
db = SQLAlchemy(app)

# Create connection variable
# conn = 'mongodb://localhost:27017'
conn = 'mongodb://trafficaquser:taq1234@ds133202.mlab.com:33202/trafficaq'

# Pass connection to the pymongo instance.
client = pymongo.MongoClient(conn)

# Connect to a database. Will create one if not already available.
# db = client.traffic_db
mdb = client.trafficaq

# Drops collection if available to remove duplicates
mdb.trafficAQ.drop()

class AQI(db.Model):
    __tablename__ = 'aqi'

    id = db.Column(db.Integer, primary_key=True)
    Latitude = db.Column(db.String)
    Longitude = db.Column(db.String)
    UTC = db.Column(db.String)
    Parameter = db.Column(db.String)
    Unit = db.Column(db.String)
    Value = db.Column(db.Float)
    AQI = db.Column(db.Integer)
    SiteName = db.Column(db.String)
    
    def __repr__(self):
        return '<AQI %r>' % (self.name)

# Create database table before any request
@app.before_first_request
def setup():
    # Recreate database each time for demo
    db.drop_all()
    db.create_all()

# Flask Routes
@app.route("/")
def home():
    """Render Home Page."""
    # return render_template("index.html")
    return render_template('form.html')

@app.route("/home", methods=["GET", "POST"])
def homeback():
    """Render Home Page."""
    # return render_template("index.html")
    return render_template('form.html')    

@app.route('/traffic.html')
def main():
    return render_template('traffic.html')

@app.route("/aqi_24")
def aqi_24_data():
    """Return aqi data"""

    # Fetch aqi data for the last 24 hours
    aqi_data = aqi2json()
    df = aqi_data.loc[aqi_data['SiteName']=="Cicero2"]

    # Add aqi data to the database
    times = []
    aqis = []
    for index, row in df.iterrows():
        new_entry = AQI(
          Latitude = row['Latitude'],
          Longitude = row['Longitude'],
          UTC = row['UTC'],
          Parameter = row['Parameter'],
          Unit = row['Unit'],
          Value = row['Value'],
          AQI = row['AQI'],
          SiteName = row['SiteName'],
        )
        db.session.add(new_entry)
        db.session.commit()
        times.append(row['UTC'])
        aqis.append(row['AQI'])

    # Generate the plot trace
    plot_trace = {
        "x": times,
        "y": aqis,
        "type": "bar",
        "name": "hourly AQI",
        # "mode": 'lines+markers',
        "marker": {
            # "color": "#2077b4",
            "color": 'rgb(9,56,125)',
            # "symbol": "hexagram"
        },
        # "line": {
        #     "color": "#17BECF"
        # },
        "text": "hourly AQI",
    }
    return jsonify(plot_trace)

@app.route("/load", methods=["GET", "POST"])
def load():

    if request.method == "POST":
        startDate = request.form["startDate"]
        endDate = request.form["endDate"]


    metaList = []
    metaUrl = "https://data.cityofchicago.org/resource/8v9j-bter.json?$limit=1500"
    response = requests.get(metaUrl)
    metaData = response.json()

    for data in metaData:
        metaDict = {}
        metaDict["segmentid"] = data.get('segmentid')
        metaDict["coordinates"] = [data.get('_lif_lat'), data.get('start_lon'),data.get('_lit_lat'), data.get('_lit_lon')] 
        metaList.append(metaDict)
    
    trafficUrl = "https://data.cityofchicago.org/resource/kkgn-a2j4.json?$where=last_update%20between%20%272018-03-13T09:30:00%27%20and%20%272018-03-13T09:40:00%27&$limit=1500"


    trafficUrl = "https://data.cityofchicago.org/resource/kkgn-a2j4.json?$where=last_update%20between%20%272018-03-13%27%20and%20%272018-03-14%27&$limit=1500"

    trafficUrl = (f"https://data.cityofchicago.org/resource/kkgn-a2j4.json?$where=last_update%20between%20%27{startDate}%27%20and%20%27{endDate}%27&$limit=1500")

    print(trafficUrl)


    response = requests.get(trafficUrl)
    trafficData = response.json()
    trafficList = []

    for data in trafficData:
        trafficDict = {}
        trafficDict["segmentid"] = data.get('segment_id')
        trafficDict["coordinates"] = [d.get('coordinates') for d in metaList if d.get('segmentid') == data.get('segment_id')]
        trafficList.append(trafficDict)
        trafficDict["traffic"] = data.get('traffic')

    mdb.traffic.insert_many(trafficList)

    print("done traffic")
    print("start aq")
    aqUrl = (f"https://aqs.epa.gov/api/rawData?user=thomas.e.abraham@gmail.com&pw=khakiosprey52&format=AQCSV&param=81102&bdate=20180601&edate=20180608&state=17&county=031")
    print(aqUrl)

    # response = requests.get(aqUrl)
    # aqData = response.json()
    # print(f"aqData length {len(aqData)}")
    # db.aq.insert_many(aqData)

    return render_template("index.html")
    print("Server received request for 'load' page...")
    return "Welcome to my 'load' page!"

@app.route("/noload", methods=["GET", "POST"])
def noload():
    return render_template("index.html")

@app.route("/history", methods=["GET", "POST"])
def history():
    # historyURL = "https://teabraham.github.io/Assignments/aqsd3/"
    # https://teabraham.github.io/Assignments/aqidash/
    
    return render_template("history.html", iframe="https://teabraham.github.io/Assignments/aqidash/")
  

if __name__ == '__main__':
    app.run(debug=True)