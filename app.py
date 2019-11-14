import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

# Import Flask
from flask import Flask, jsonify

# Create an app, pass __name__
app = Flask(__name__)

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Definition of index route
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date"
    )

# Definition of precipitation route
@app.route("/api/v1.0/precipitation")
def precip():
    print("Server received request for 'precipitation' page...")

    session = Session(engine)
    precips = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > "2016-08-22").all()
    session.close()

    precipitation_last_year = []
    for precip in precips:
        precip_dict = {}
        precip_dict[precip.date] = precip.prcp
        precipitation_last_year.append(precip_dict)

    return jsonify(precipitation_last_year)

# Definition of station route
@app.route("/api/v1.0/stations")
def station():
    print("Server received request for 'station' page...")

    session = Session(engine)
    stations = session.query(Measurement.station).group_by(Measurement.station).all()
    session.close()

    all_stations = list(np.ravel(stations))
    return jsonify(all_stations)

# Definition of temperature route
@app.route("/api/v1.0/tobs")
def temp():
    print("Server received request for 'temperature' page...")

    session = Session(engine)
    temps = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == "USC00519281", Measurement.date > "2016-08-22").all()
    session.close()

    temperature_last_year = []
    for temp in temps:
        temp_dict = {}
        temp_dict[temp.date] = temp.tobs
        temperature_last_year.append(temp_dict)

    return jsonify(temperature_last_year)

# Definition of start date route
@app.route("/api/v1.0/<start_date>")
def start(start_date):

    session = Session(engine)
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= start_date).group_by(Measurement.date).all()
    session.close()

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)

    return jsonify(dates)

# Definition of between date route
@app.route("/api/v1.0/<start_date>/<end_date>")
def startEnd(start_date, end_date):
    
    session = Session(engine)
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= start_date).filter(func.strftime("%Y-%m-%d", Measurement.date) <= end_date).\
        group_by(Measurement.date).all()
    session.close()

    between_dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        between_dates.append(date_dict)

    return jsonify(between_dates)

if __name__ == "__main__":
    app.run(debug=True)
