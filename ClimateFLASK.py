# Import relevant libaries and functions

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import pandas as pd
import datetime as dt
from flask import Flask, jsonify

# Create an engine to connect to the hawaii.sqlite data
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})

# Define the base to reflect with table information regarding 'Measurement' and 'Station'
Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

Station = Base.classes.station
Measurement = Base.classes.measurement

session = Session(engine)

# Online Weather Application
# Retreiving the current date and One Year Ago date with datetime.
app = Flask(__name__)

curtdate =  list(np.ravel((session.query(Measurement.date)
                .order_by(Measurement.date.desc())
                .first())))[0]

curtdate = dt.datetime.strptime(curtdate, '%Y-%m-%d')
curtday = int(dt.datetime.strftime(curtdate, '%d'))
curtmo = int(dt.datetime.strftime(curtdate, '%m'))
curtyr = int(dt.datetime.strftime(curtdate, '%Y'))

oneyearago = dt.date(curtyr, curtmo, curtday) - dt.timedelta(days=365)
oneyearago = dt.datetime.strftime(oneyearago, '%Y-%m-%d')

# Set up the webpage routes
@app.route('/')
def homepage():
    return (f"""
            Surf's Up! Homepage: Hawai Climate API <br/>
            ---------------------------------------------- <br/>
            Avaliable Routes (Table of Contents) <br/> <br/>
            /api/v1.0/precipitation : Precipitation data for the last year <br/>
            /api/v1.0/stations : List of all weather observation stations in database <br/>
            /api/v1.0/tobs : Temperature data for the last year <br/>
            /api/v1.0/datesearch/<start> : Return a JSON list of the minimum, average, and maximum temperature for the given start date to present (between August 23rd, 2016 and 2017) <br/>
            ** After the above route, add the date of your choice in a YYYY-MM-DD format. ** <br/>
            /api/v1.0/datesearch/<start>/<end> : Calculate the above for days between the start and end date given
            """)

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Query sessions for all of the data regarding precipitaton measurements, dates, and station IDs
    prcpRslts = (session.query(Measurement.date, Measurement.prcp, Measurement.station)
                      .filter(Measurement.date > oneyearago)
                      .order_by(Measurement.date)
                      .all())

    # Create a list of dictionaries with the result date, precipitation, and Station ID
    prcpLst = []
    for Rslt in prcpRslts:
        prcpDict = {Rslt.date: Rslt.prcp, 'Station ID': Rslt.station}
        prcpLst.append(prcpDict)

    return jsonify(prcpLst)

@app.route("/api/v1.0/stations")
def stations():
    staRslts = session.query(Station.station, Station.name).all()
    staRslts = list(np.ravel(staRslts))
    staLst = []

    for Rslt in staRslts:
        staDict = {Rslt.station: Rslt.name}
        staLst.append(staDict)
    #[staLst.append({Rslt.station: Rslt.name}) for Rslt in staRslts]

    return jsonify(staLst)

@app.route('/api/v1.0/datesearch/<start>')
def start(start):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= start)
                       .group_by(Measurement.date)
                       .all())

    dates = []                       
    for Rslt in Rslts:
        dateDict = {}
        dateDict["Date"] = Rslt[0]
        dateDict["Low Temp"] = Rslt[1]
        dateDict["Avg Temp"] = Rslt[2]
        dateDict["High Temp"] = Rslt[3]
        dates.append(dateDict)
    return jsonify(dates)

@app.route('/api/v1.0/datesearch/<start>/<end>')
def startEnd(start, end):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= start)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) <= end)
                       .group_by(Measurement.date)
                       .all())

    dates = []                       
    for Rslt in Rslts:
        dateDict = {}
        dateDict["Date"] = Rslt[0]
        dateDict["Low Temp"] = Rslt[1]
        dateDict["Avg Temp"] = Rslt[2]
        dateDict["High Temp"] = Rslt[3]
        dates.append(dateDict)
    return jsonify(dates)

# Run the webpage application
if __name__=='__main__':
    app.run(debug=True)