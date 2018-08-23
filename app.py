# Flask and database setup
import pandas as pd
from flask import (
    Flask,
    render_template,
    jsonify)
from flask_sqlalchemy import SQLAlchemy
from aqi2json import aqi2json

# Flask Setup
app = Flask(__name__)

# Database Setup
# The database URI
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db/aqi.sqlite"
db = SQLAlchemy(app)

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
    return render_template("index.html")

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

if __name__ == '__main__':
    app.run(debug=True)