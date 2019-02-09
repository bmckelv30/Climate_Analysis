import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt


from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite?check_same_thread=False")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
Base.classes.keys()

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
    return (
        f"Welcome to the Hawaii climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    results = session.query(Measurement.date, Measurement.prcp).all()
    
    all_prcp = []
    for precipitation in results:
        precipitation_dict = {}
        precipitation_dict["date"] = precipitation.date
        precipitation_dict["prcp"] = precipitation.prcp
        all_prcp.append(precipitation_dict)
        
    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Measurement.station).all()
    
    all_stations = []
    for station in results:
        stations_dict = {}
        stations_dict["station"] = station.station
        all_stations.append(stations_dict)
        
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    last_date = session.query(func.max(Measurement.date)).first()
    date_lt = dt.datetime.strptime(str(last_date), "('%Y-%m-%d',)")
    year_ago = date_lt - dt.timedelta(days=365)
    
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > year_ago).\
        group_by(Measurement.date).\
        order_by(Measurement.date).all()
    
    tobs_yr = []
    for temp in results:
        temps_dict = {}
        temps_dict["date"] = temp.date
        temps_dict["tobs"] = temp.tobs
        tobs_yr.append(temps_dict)
        
    return jsonify(tobs_yr)

@app.route("/api/v1.0/<start>")
def temps_start(start):
    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()

    tobs_yr = []
    for temp in results:
        temps_dict = {}
        temps_dict["TMIN"] = temp[0]
        temps_dict["TAVG"] = temp[1]
        temps_dict["TMAX"] = temp[2]
        tobs_yr.append(temps_dict)  
    return jsonify(tobs_yr)

                
@app.route("/api/v1.0/<start>/<end>")
def start_to_end_temps(start,end):
    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    temp_yr = []
    for tmp in results:
        tmp_dict = {}
        tmp_dict["TMIN"] = tmp[0]
        tmp_dict["TAVG"] = tmp[1]
        tmp_dict["TMAX"] = tmp[2]
        temp_yr.append(tmp_dict)  
    return jsonify(temp_yr)

if __name__ == "__main__":
    app.run(debug=True)