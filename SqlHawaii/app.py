import pandas as pd
import numpy as np
import os
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()
print(Base.classes.keys())

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)


app = Flask(__name__)


@app.route("/")
def welcome():
    return (
        f"This is the home page of Hawaii climate analysis<br/>"
        f"The following are the available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the JSON representation of dictionary for the last year."""
    
    # To find the last day:

    lastday = list(np.ravel(session.query(Measurement.date).order_by(Measurement.date.desc()).first()))[0]
    lastday = lastday.split("-")
    year = int(lastday[0])
    month = int(lastday[1])
    day = int(lastday[2])

    # To find 1 year before the last day:

    lastyear = dt.date(year, month, day) - dt.timedelta(days=365)

    precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= lastyear).order_by(Measurement.date).all()

    precipitation_dic = {date: i for date, i in precipitation}

    return jsonify(precipitation_dic)


@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""

    stations = list(np.ravel(session.query(Station.station).all()))

    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of Temperature Observations (tobs) for the previous year."""

    # To find the last day:

    lastday = list(np.ravel(session.query(Measurement.date).order_by(Measurement.date.desc()).first()))[0]
    lastday = lastday.split("-")
    year = int(lastday[0])
    month = int(lastday[1])
    day = int(lastday[2])

    # To find 1 year before the last day:

    lastyear = dt.date(year, month, day) - dt.timedelta(days=365)

    activestations = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    mostactiveid = activestations[0][0]

    temperatures = list(np.ravel(session.query(Measurement.tobs).filter(Measurement.station == mostactiveid).filter(Measurement.date >= lastyear).all()))

    return jsonify(temperatures)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def trip(start=None, end=None):
    """Return min, max, and average temperature during the trip"""

    if not end:

        lowesttemp = session.query(Measurement.tobs).filter(Measurement.date >= start).order_by(Measurement.tobs.asc()).first()
        highesttemp = session.query(Measurement.tobs).filter(Measurement.date >= start).order_by(Measurement.tobs.desc()).first()
        averagetemp = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start).first()
        results = list(np.ravel([lowesttemp, highesttemp, averagetemp]))

        return jsonify(results)


    lowesttemp = session.query(Measurement.tobs).filter(Measurement.date >= start).filter(Measurement.date <= end).order_by(Measurement.tobs.asc()).first()
    highesttemp = session.query(Measurement.tobs).filter(Measurement.date >= start).filter(Measurement.date <= end).order_by(Measurement.tobs.desc()).first()
    averagetemp = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).first()
    results = list(np.ravel([lowesttemp, highesttemp, averagetemp]))

    return jsonify(results)


if __name__ == '__main__':
    app.run()


