# Import the dependencies.
from flask import Flask, jsonify
import datetime as dt
import sqlalchemy
from sqlalchemy.types import Date
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from sqlalchemy import create_engine, func, Column, Integer, String, Float , and_
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta



#################################################
# Database Setup
#################################################

Base = declarative_base()

# Create Classes for Measurement and Station

class Measurement(Base):
    __tablename__ = "measurement"
    
    id = Column(Integer, primary_key=True)
    station = Column(String)
    date = Column(Date)
    prcp = Column(Float)
    tobs = Column(Float)

class Station(Base):
    __tablename__ = "station"
    
    id = Column(Integer, primary_key=True)
    station = Column(String)
    name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    elevation =  Column(Float)

# reflect an existing database into a new model

# reflect the tables

# Save references to each table

# Create our session (link) from Python to the DB

Engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Conn = Engine.connect()

session = scoped_session(sessionmaker(bind=Engine))

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route('/')
def welcome():
    """All available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"Temperature for one year: /api/v1.0/tobs<br/>"
        f"Temperature stat from the start date(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature stat from start to end dates(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

@app.route('/api/v1.0/precipitation')
def Precipitation():
    session1 = Session(Engine)

# Calculate the date one year ago from the most recent date in the database

    most_recent_date = session1.query(func.max(Measurement.date)).scalar()

    most_recent_date_str = most_recent_date.strftime('%Y-%m-%d')

    twelve_months_ago = (datetime.strptime(most_recent_date_str, '%Y-%m-%d') - timedelta(days=365)).strftime('%Y-%m-%d')

# Define the columns to be selected

    sel = [Measurement.date, Measurement.prcp]

# Query precipitation data for the last 12 months

    qresult = session1.query(*sel).filter(and_(Measurement.date >= twelve_months_ago, Measurement.date <= most_recent_date_str)).all()

    session1.close()

    Precipitation = []

    for date, prcp in qresult:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        Precipitation.append(prcp_dict)

    return jsonify(Precipitation)



@app.route('/api/v1.0/stations')
def Stations():
    session2 = Session(Engine)

# Define the columns to be selected

    sel = [Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation]

    qresult = session2.query(*sel).all()

    session2.close()

    Stations = []
    for station,name,lat,lon,el in qresult:
        Station_dict = {}
        Station_dict["Station"] = station
        Station_dict["Name"] = name
        Station_dict["Lat"] = lat
        Station_dict["Lon"] = lon
        Station_dict["Elevation"] = el
        Stations.append(Station_dict)

    return jsonify(Stations)

@app.route('/api/v1.0/tobs')
def Tobs():

    Tobs_station = session.query(Measurement.station, Measurement.tobs)\
    .filter(Measurement.date > '2016-08-23')\
    .filter(Measurement.date <= '2017-08-23')\
    .filter(Measurement.station == "USC00519281")\
    .order_by(Measurement.date).all()


    Tobs_dict = dict(Tobs_station)

   
    return jsonify(Tobs_dict)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_date(start, end=None):
    try:
# Convert start and end dates to datetime objects

        start_date = datetime.strptime(start, "%Y-%m-%d")

        if end:
            end_date = datetime.strptime(end, "%Y-%m-%d")
        else:
            end_date = datetime.now()

# Query for temperature statistics

        temperature_stats = (
            session.query(
                func.min(Measurement.tobs),
                func.max(Measurement.tobs),
                func.round(func.avg(Measurement.tobs)),
            )
            .filter(Measurement.date.between(start_date, end_date))
            .first()
        )

# Handle the case when there are no results

        if not temperature_stats:
            return jsonify({"error": "No data found for the specified date range."})

        keys = ["Min Temp", "Max Temp", "Avg Temp"]
        temp_dict = {keys[i]: temperature_stats[i] for i in range(len(keys))}

        return jsonify(temp_dict)

    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."})


if __name__ == '__main__':
    app.run(debug=True)