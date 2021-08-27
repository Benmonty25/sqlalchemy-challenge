import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

# DB setup
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database
base = automap_base()

# reflect the tables
base.prepare(engine, reflect=True)

# table references
measurement = base.classes.measurement
station = base.classes.station

# flask setup

app = Flask(__name__)

@app.route("/")
def welcome():
    """Available Routes."""
    return (
        f"Welcome to my SQL-Alchemy APP!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]<br/>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]/[end_date format:yyyy-mm-dd]<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
 # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all Precipitation Data"""
    # Query all Precipitation
    precipitation = session.query(measurement.date, measurement.prcp).\
        order_by(measurement.date).all()
    session.close()
    
    # Convert the list to Dictionary
    precipitation_data = []
    for date, prcp in precipitation:
        info = {}
        info['date'] = date
        info['prcp'] = prcp
        precipitation_data.append(info)
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session
    session = Session(engine)

    """Return a list of all Stations"""
    # Pull all Stations
    all_stations = session.query(station.station).\
                 order_by(station.station).all()

    session.close()

    # Convert list
    all_stations = list(np.ravel(all_stations))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session
    session = Session(engine)

    """Return a list of all Temperatures"""
    # Pull all tobs for last year  
    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()

    last_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    first_date = last_date - dt.timedelta(days=365)

    # Perform a query to retrieve the last year of data and temperatures
    temperatures = session.query(measurement.date,measurement.tobs).\
                filter(measurement.station=='USC00519281').\
                filter(measurement.date >= first_date).\
                order_by(measurement.date).all()

    session.close()

    # Convert the list to Dictionary
    all_tobs = []
    for date,tobs in temperatures:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs

        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

    
@app.route("/api/v1.0/<start_date>")
def Start_date(start_date):
    # Create our session 
    session = Session(engine)

    """Return a list of minimum, average and max temperatures for a start date"""
    # Query tobs greater than start date

    query = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                filter(measurement.date >= start_date).all()

    session.close()

    # Create a dictionary from the row data and append to a list of date_tobs
    date_tobs = []
    for min, avg, max in query:
        date_tobs_dict = {}
        date_tobs_dict["TMIN"] = min
        date_tobs_dict["TAVG"] = avg
        date_tobs_dict["TMAX"] = max
        date_tobs.append(date_tobs_dict) 
    return jsonify(date_tobs)

@app.route("/api/v1.0/<start_date>/<end_date>")
def Start_end_date(start_date, end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of minimum, average and max temperatures for start and end dates"""
    # Query all tobs

    query = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                filter(measurement.date >= start_date).\
                filter(measurement.date <= end_date).all()

    session.close()
  
    # Create a dictionary from the row data and append to a list of start_end_date_tobs
    startenddate_tobs = []
    for min, avg, max in query:
        startenddate_tobs_dict = {}
        startenddate_tobs_dict["TMIN"] = min
        startenddate_tobs_dict["TAVG"] = avg
        startenddate_tobs_dict["TMAX"] = max
        startenddate_tobs.append(startenddate_tobs_dict) 
    

    return jsonify(startenddate_tobs)

if __name__ == "__main__":
    app.run(debug=True)