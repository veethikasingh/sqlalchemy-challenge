
#Now that you’ve completed your initial analysis, you’ll design a
#Flask API based on the queries that you just developed. To do
#so, use Flask to create your routes as follows:

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


engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# reflect the tables

Base.classes.keys()
# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session= Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
#1 Home Page#

@app.route("/")

def welcome():
#List all available api routes

 return (
    "<div style='text-align: center; color: green; font-family: Arial, sans-serif;'>"
    "<h1>Welcome to the Climate App for Hawaii</h1>"       
    "<div style='display: flex; flex-direction: column; align-items: center;'>" 


        f"Available Routes for Hawaii Weather Data:<br/><br>"
        f"-- Daily Precipitation Totals for Last Year: <a href=\"/api/v1.0/precipitation\">/api/v1.0/precipitation<a><br/>"
        f"-- Active Weather Stations: <a href=\"/api/v1.0/stations\">/api/v1.0/stations<a><br/>"
        f"-- Most active Station USC00519281-WAIHEE: <a href=\"/api/v1.0/tobs\">/api/v1.0/tobs<a><br/>"
        f"-- Min, Average & Max Temperatures greater than date: <a href=\"/api/v1.0/&lt;start&gt\">/api/v1.0/&lt;start&gt</a><br/>"
        f"-- Min, Average & Max Temperatures for date range: <a href=\"/api/v1.0/&lt;start&gt;/&lt;end&gt\">/api/v1.0/&lt;start&gt;/&lt;end&gt</a><br/>"
        "</div>"
        "</div>"
    )  

#2 last 12 months of data using date and precipitation  

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Return a list of all daily precipitation totals for the last year
    
    
    start_date = '2016-08-23'
    sel = [measurement.date, 
        func.sum(measurement.prcp)]
    precipitation = session.query(*sel).\
            filter(measurement.date >= start_date).\
            order_by(measurement.date).all()
   #            group_by(measurement.date).\
    
    session.close()
    # FIll dictionary with the date as key and the daily precipitation total as value
    precipitation_dates = []
    precipitation_totals = []
    for date, dailytotal in precipitation:
        precipitation_dates.append(date)
        precipitation_totals.append(dailytotal)
    
    precipitation_dict = dict(zip(precipitation_dates, precipitation_totals))

    return jsonify(precipitation_dict)

#3.  list of stations from the dataset

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_no = session.query(station.station,station.name).all()
    session.close()
    station_data = {station: name for station,name in station_no}
    return jsonify(station_data)

#4. list of temperature observations for the previous year of most active station.
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query the last 12 months of temperature observation data for the most active station
    start_date = '2016-08-23'
    sel = [measurement.date, 
        measurement.tobs]
    station_temps = session.query(*sel).\
            filter(measurement.date >= start_date, measurement.station == 'USC00519281').\
            group_by(measurement.date).\
            order_by(measurement.date).all()

    session.close()

    # fill dictionary with the date as key and the daily temperature observation as value
    observation_dates = []
    temperature_observations = []

    for date, observation in station_temps:
        observation_dates.append(date)
        temperature_observations.append(observation)
    
    most_active_tobs_dict = dict(zip(observation_dates, temperature_observations))

    return jsonify(most_active_tobs_dict)

#5 average temperature, and the maximum temperature for a specified start or start-end range.


@app.route("/api/v1.0/<start>")
def trip1(start):
    # Calculate minimum, average and maximum temperatures for the range of dates starting with start date.
    

    session = Session(engine)
    query_result = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).all()
    #.filter(measurement.date <= end_date)
    session.close()

    trip_stats = []
    for min, avg, max in query_result:
        trip_dict = {}
        trip_dict["Min"] = min
        trip_dict["Average"] = avg
        trip_dict["Max"] = max
        trip_stats.append(trip_dict)

    # If the query returned non-null values return the results,
    # otherwise return a message
    if trip_dict['Min']: 
        return jsonify(trip_stats)
    else:
        return jsonify({"Input Required": f"Enter Date formatted as YYYY-MM-DD."}), 404
 
 
# Route with both dates as input     
@app.route("/api/v1.0/<start>/<end>")
def start_date_endtrip2(start,end):
    # Calculate minimum, average and maximum temperatures for the range of dates starting with start date.
   

    session = Session(engine)

    query_result = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= end).all()
   
    session.close()

    trip_stats = []
    for min, avg, max in query_result:
        trip_dict = {}
        trip_dict["Min"] = min
        trip_dict["Average"] = avg
        trip_dict["Max"] = max
        trip_stats.append(trip_dict)

    # If the query returned non-null values return the results,
    # otherwise return a message
    if trip_dict['Min']: 
        return jsonify(trip_stats)
    else:
        return jsonify({"Input Required": f"Enter Date in YYYY-MM-DD format"}), 404
  

if __name__ == '__main__':
    app.run(debug=True)