import numpy as np
import pandas as pd
import datetime as dt

# # Reflect Tables into SQLAlchemy ORM
# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, distinct

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

from dateutil.relativedelta import relativedelta
start_date = dt.date(2017,8,23) - relativedelta(years=1)

app = Flask(__name__)

@app.route("/")
def home():
    return (
        f"Welcome. Here are the available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/'<start>'<br/>"
        f"/api/v1.0/'<start>'/'<end>'<br/>"
            )

@app.route("/api/v1.0/precipitation")
def Precipitation():
    session = Session(engine)
    prcp_bydate = session.query(Measurement.date, func.sum(Measurement.prcp)). \
                    filter(Measurement.date > start_date).group_by(Measurement.date).order_by(Measurement.date).all()
    prcp_list = []
    for date, prcp in prcp_bydate:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["precipi"] = prcp
        prcp_list.append(prcp_dict)
    return jsonify(prcp_list)

@app.route("/api/v1.0/stations")
def Stations():
    session = Session(engine)
    station_results = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
    station_list = []
    for station, name, lat, lng, elev in station_results:
        station_dict = {}
        station_dict["station_code"] = station
        station_dict["name"] = name
        station_dict["latitude"] = lat
        station_dict["longitude"] = lng
        station_dict["elevation"] = elev
        station_list.append(station_dict)
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def Tempreture():
    session = Session(engine)
    temp_results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > start_date).all()
    temp_list = []
    for date, tobs in temp_results:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["tempreture"] = tobs
        temp_list.append(temp_dict)
    return jsonify(temp_list)

@app.route("/api/v1.0/<start_date>")
def calc_temps_start(start_date):
    session = Session(engine)
    temp_start_dates = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start_date).all()
    temp_start_list = []
    for tmin, tavg, tmax in temp_start_dates:
        temp_start_dict = {}
        temp_start_dict["Min Temp"] = tmin
        temp_start_dict["Avg Temp"] = tavg
        temp_start_dict["Max Temp"] = tmax
        temp_start_list.append(temp_start_dict)
    return jsonify(temp_start_list)

@app.route("/api/v1.0/<start_date>/<end_date>")
def calc_temps(start_date, end_date):
    session = Session(engine)
    temp_bwdates = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    temp_bw_list = []
    for tmin, tavg, tmax in temp_bwdates:
        temp_bw_dict = {}
        temp_bw_dict["Min Temp"] = tmin
        temp_bw_dict["Avg Temp"] = tavg
        temp_bw_dict["Max Temp"] = tmax
        temp_bw_list.append(temp_bw_dict)
    return jsonify(temp_bw_list)

if __name__ == '__main__':
    app.run(debug=True)