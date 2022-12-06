#imports/dependencies
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#access sqlite db
engine = create_engine('sqlite:///hawaii.sqlite')

#reflect db into classes
Base = automap_base()
Base.prepare(engine, reflect=True)

#tables to classes
Measurement = Base.classes.measurement
Station = Base.classes.station

#start session for queries
session = Session(engine)

#set up flask
app = Flask(__name__)

#welcome route
@app.route('/')
def welcome():
    return(
    '''
    Welcome to the Climate Analysis API!\n

    Available Routes:\n

    /api/v1.0/precipitation\n

    /api/v1.0/stations\n

    /api/v1.0/tobs\n

    /api/v1.0/temp/start/end\n
    ''')

#precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    #time frame var
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    #filtered precipipitation query assigned to var
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()

    #loop over prev var to create dict assigned to var
    precip = {date: prcp for date, prcp in precipitation}

    #return as json
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    #query assigned to var
    results = session.query(Station.station).all()

    #unravel query var into list var
    stations = list(np.ravel(results))

    #returns as json, arg to format list into json
    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def temp_monthly():
    #time frame var
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    #filtered query assigned to var
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == "USC00519281").\
        filter(Measurement.date >= prev_year).all()

    #unravel query var into list var
    temps = list(np.ravel(results))

    #return as json
    return jsonify(temps=temps)

#requires args provided in url/api call
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    #list of queries to make: min, avg and max temp obs
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    #idk, check if an end arg was provided, if not then:?
    if not end:
        #query all from var list cel, filter according to start arg, and save to var
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()

        temps = list(np.ravel(results))

        #return
        return jsonify(temps=temps)

    #calc min, avg and max temps with start and end dates
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    temps = list(np.ravel(results))

    #return
    return jsonify(temps=temps)


