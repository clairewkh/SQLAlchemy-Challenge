#import dependencies

from flask import Flask, jsonify
import numpy as np
import sqlalchemy
import datetime as dt
from sqlalchemy import inspect, create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

#Setting up Database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#Reflect an existing database and tables
Base = automap_base()
Base.prepare(engine, reflect=True)

#Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#creating an app
app = Flask(__name__)

#Homepage
@app.route('/')
def home_page():
    """List all the avaliable api routes"""
    return(
        'This is the Homepage and below are all the avaliable routes<br/>'
        f"<br/>"  
        f'/api/v1.0/precipitation<br/>'
        f"<br/>"  
        f'/api/v1.0/stations<br/>'
        f"<br/>"  
        f'/api/v1.0/tobs<br/>'
        f"<br/>"  
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"<br/>"  
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    ) 

#precipitation page
@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)

    """Return the dictionary for date and precipitation info"""
    date_new = session.query(func.max(Measurement.date)).scalar()

    date_last_year = dt.datetime.strptime(date_new, '%Y-%m-%d') - dt.timedelta(days = 365)
    date_last_year = date_last_year.strftime('%Y-%m-%d')

    results = session.query(Measurement.date, Measurement.prcp).\
            filter(Measurement.date >= date_last_year).all()
        
    session.close()
    
    precipitation = []
    for date,prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation )

#stations page
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    results1 = session.query(Station.name).all()

    session.close()

    station_list = []
    for station in results1:
        station_list.append(station)

    return jsonify(station_list)

#temperature page
@app.route("/api/v1.0/tobs")
def tobs1():
    session = Session(engine)

    date_new = session.query(func.max(Measurement.date)).scalar()

    date_last_year = dt.datetime.strptime(date_new, '%Y-%m-%d') - dt.timedelta(days = 365)
    date_last_year = date_last_year.strftime('%Y-%m-%d')

    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    station_id_active = active_stations[0][0]

    results2 = session.query(Measurement.date, Measurement.tobs)\
                .filter(Measurement.date > date_last_year)\
                .filter(Measurement.station == station_id_active)

    session.close()

    tobs_list = []
    for date, tobs in results2:
        tobs_dict = {}
        tobs_dict[date] = tobs
        tobs_list.append(tobs_dict)


    return jsonify(tobs_list)

#temp_info page 
@app.route("/api/v1.0/<start>")
def temp_start(start):
    session = Session(engine)

    results3 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    start_info = []
    for min,avg,max in results3:
        start_dict = {}
        start_dict["T Min:"] = min
        start_dict["T Average:"] = round(avg,4)
        start_dict["T Max:"] = max
        start_info.append(start_dict)

    return jsonify(start_info)

#temp_info page2
@app.route('/api/v1.0/<start>/<end>')
def temp_between(start, end):
    session = Session(engine)

    results4 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    between_info = []
    for min,avg,max in results4:
        between_dict = {}
        between_dict["T Min"] = min
        between_dict["T Average"] = round(avg,4)
        between_dict["T Max"] = max
        between_info.append(between_dict)

    return jsonify(between_info)


if __name__ == "__main__":
    app.run(debug=True)

    