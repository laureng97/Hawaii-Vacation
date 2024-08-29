# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
import re

# Python SQL Toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, text
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with = engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

# Find the most recent date in the data set
# 1. /
#Start at the homepage.
#List all the available routes.

@app.route("/")
def home():
    return(
        f"Welcome to the Sql Alchemy Hawaii Climate Analysis API! <br/>"
        f"Available Routes: <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

# 2. /api/v1.0/precipitation
# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session (engine)

    # Design a query to retrieve the last 12 months of precipitation data and plot the results. 
    # Starting from the most recent data point in the database. 
    twelve_months = dt.date(2017, 8, 23)-dt.timedelta(days=365)

    # Calculate the date one year from the last date in data set.
    previous_date = dt.date(twelve_months.year, twelve_months.month, twelve_months.day)

    # Perform a query to retrieve the data and precipitation scores
    scores = session.query(Measurement.date, Measurement.prcp).filter(
        Measurement.date >= previous_date).order_by(Measurement.date).all()
    
    # Create the dictionary 
    precipitation_dict = dict(scores)

    # Print the json representation of the dictionary
    print(f"These are the results for precipitation: {precipitation_dict}")
    print("Out of the precipitation section.")

    return jsonify(precipitation_dict)

# 3. /api/v1.0/stations
# Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations_data = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
    stations_result = session.query(*stations_data).all()
    session.close()

    stations = []
    for station,name,lat,lon,el in stations_result:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        stations.append(station_dict)

    return jsonify(stations)

# 4. /api/v1.0/tobs
# Query the dates and temperature observations of the most-active station for the previous year of data.
# Return a JSON list of temperature observations for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    tobs_result = session.query( Measurement.date, Measurement.tobs).filter(Measurement.station=='USC00519281')\
     .filter(Measurement.date>='2016-08-23').all()


    tob_data = []
    for date, tobs in tobs_result:
         tobs_dict = {}
         tobs_dict["Date"] = date
         tobs_dict["Tobs"] = tobs
         tob_data.append(tobs_dict)

    return jsonify(tob_data)

# 5. /api/v1.0/<start> and /api/v1.0/<start>/<end>
# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.

@app.route("/api/v1.0/<start>")
def temps_start(start):
    session= Session(engine)
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    temps = []
    for min_temp, avg_temp, max_temp in temp_data:
        temps_dict = {}
        temps_dict['Minimum Temperature'] = min_temp
        temps_dict['Average Temperature'] = avg_temp
        temps_dict['Maximum Temperature'] = max_temp
        temps.append(temps_dict)

    return jsonify(temps)

@app.route("/api/v1.0/<start>/<end>")
def temps_start_end(start, end):
    session = Session(engine)
    temp_data_se = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    temps_se = []
    for min_temp, avg_temp, max_temp in temp_data_se:
        temps_se_dict = {}
        temps_se_dict['Minimum Temperature'] = min_temp
        temps_se_dict['Average Temperature'] = avg_temp
        temps_se_dict['Maximum Temperature'] = max_temp
        temps_se.append(temps_se_dict)

    return jsonify(temps_se)


if __name__ == '__main__':
    app.run(debug=True)