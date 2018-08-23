from flask import Flask, render_template, request, redirect
import requests
import json
# Import our pymongo library, which lets us connect our Flask app to our Mongo database.
import pymongo

# 2. Create an app, being sure to pass __name__
app = Flask(__name__)


# Create connection variable
conn = 'mongodb://localhost:27017'

# Pass connection to the pymongo instance.
client = pymongo.MongoClient(conn)

# Connect to a database. Will create one if not already available.
# db = client.traffic_db
db = client.trafficAQ_db

# Drops collection if available to remove duplicates
db.trafficAQ.drop()

# # Creates a collection in the database and inserts two documents
# db.team.insert_many(
#     [
#         {
#             'player': 'Jessica',
#             'position': 'Point Guard'
#         },
#         {
#             'player': 'Mark',
#             'position': 'Center'
#         }
#     ]
# )


# 3. Define what to do when a user hits the index route
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
        # Store the entire team collection in a list
    # teams = list(db.team.find())
    # print(teams)

    # Return the template with the teams list passed in
    return render_template('form.html')
    # return "Welcome to my 'Home' page!"


# 4. Define what to do when a user hits the /about route
@app.route("/load", methods=["GET", "POST"])
def load():

    if request.method == "POST":
        startDate = request.form["startDate"]
        endDate = request.form["endDate"]


    metaList = []
    metaUrl = "https://data.cityofchicago.org/resource/8v9j-bter.json?$limit=2000"
    response = requests.get(metaUrl)
    metaData = response.json()

    for data in metaData:
        metaDict = {}
        metaDict["segmentid"] = data.get('segmentid')
        metaDict["coordinates"] = [data.get('_lif_lat'), data.get('start_lon'),data.get('_lit_lat'), data.get('_lit_lon')] 
        metaList.append(metaDict)
    
    trafficUrl = "https://data.cityofchicago.org/resource/kkgn-a2j4.json?$where=last_update%20between%20%272018-03-13T09:30:00%27%20and%20%272018-03-13T09:40:00%27&$limit=1500"


    trafficUrl = "https://data.cityofchicago.org/resource/kkgn-a2j4.json?$where=last_update%20between%20%272018-03-13%27%20and%20%272018-03-14%27&$limit=1500"

    trafficUrl = (f"https://data.cityofchicago.org/resource/kkgn-a2j4.json?$where=last_update%20between%20%27{startDate}%27%20and%20%27{endDate}%27")

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

    db.traffic.insert_many(trafficList)

    print("done traffic")
    print("start aq")
    aqUrl = (f"https://aqs.epa.gov/api/rawData?user=thomas.e.abraham@gmail.com&pw=khakiosprey52&format=AQCSV&param=81102&bdate=20180601&edate=20180608&state=17&county=031")
    print(aqUrl)

    # response = requests.get(aqUrl)
    # aqData = response.json()
    # print(f"aqData length {len(aqData)}")
    # db.aq.insert_many(aqData)


    print("Server received request for 'load' page...")
    return "Welcome to my 'load' page!"

@app.route("/retrieveTraffic")
def retrieveTraffic():
    print("Server received request for 'retrieveTraffic' page...")
    return "Welcome to my 'retrieveTraffic' page!"

@app.route("/retrieveAQ")
def retrieveAQ():
    print("Server received request for 'retrieveAQ' page...")
    return "Welcome to my 'retrieveAQ' page!"    

@app.route("/d3", methods=["GET", "POST"])
def d3():
    return render_template("d3.html")

if __name__ == "__main__":
    app.run(debug=True)
