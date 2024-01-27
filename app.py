# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station



# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
        """Welcome to the Climate App."""
        return(
            f"Available Routes:<br/>"
            f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs<br/>"
    )

        
@app.route("/api/v1.0/precipitation")

def precipitation():
        #Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value. 
        #Return the JSON representation of your dictionary.
        session=Session(engine)
        year_ago=dt.date(2017, 8, 23)-dt.timedelta(days=365)
        one_year_previous_date =dt.date(year_ago.year, year_ago.month, year_ago.day)
        precipitation_scores = session.query(measurement.date, func.max(measurement.prcp)).\
            filter(measurement.date >= func.strftime("%Y-%m-%d", one_year_previous_date)).\
            group_by(measurement.date).order_by(measurement.date).all()
        session.close()
        
        dictionary=dict(precipitation_scores)
        return jsonify(dictionary)

@app.route("/api/v1.0/stations")
def stations():
        #Return a JSON list of stations from the dataset
    
    session = Session(engine)
    station_list = session.query(station.station,station.id).all()

    session.close()

    all_stations = list(np.ravel(station_list))

     
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
       #Query the dates and temperature observations of the most-active station for the previous year of data
       #Return a JSON list of temperature observations for the previous year.
    session = Session(engine)
        
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    one_year_previous_date = dt.date(year_ago.year, year_ago.month, year_ago.day)

    most_active_station_id = session.query(measurement.station).\
        group_by(measurement.station).\
        order_by(func.count(measurement.station).desc()).first()[0]

    year_data = session.query(measurement.tobs).filter(measurement.station == most_active_station_id).\
        filter(measurement.date > one_year_previous_date).all()
    
    session.close()
    
    return jsonify(year_data)

if __name__ == '__main__':
    app.run(debug=True)
