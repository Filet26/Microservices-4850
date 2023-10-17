from sqlalchemy import Column, Integer, String, DateTime, Float
from base import Base
import datetime


class TemperatureReading(Base):

    __tablename__ = "temperature_readings"

    id = Column(Integer, primary_key=True)
    home_id = Column(String(250), nullable=False)
    device_id = Column(String(250), nullable=False)
    ambient_temperature = Column(Float, nullable=False)
    ambient_humidity = Column(Float, nullable=False)
    outdoor_weather = Column(String(100), nullable=False)
    atmospheric_pressure = Column(Float, nullable=False)
    timestamp = Column(String(100), nullable=False)
    trace_id = Column(String(250), nullable=False)
    date_created = Column(DateTime, nullable=False)
    

    def __init__(self, home_id, device_id, timestamp, ambient_temperature, ambient_humidity, outdoor_weather, atmospheric_pressure, trace_id):
        self.home_id = home_id
        self.device_id = device_id
        self.ambient_temperature = ambient_temperature
        self.ambient_humidity = ambient_humidity
        self.outdoor_weather = outdoor_weather
        self.atmospheric_pressure = atmospheric_pressure
        self.timestamp = timestamp
        self.trace_id = trace_id
        self.date_created = datetime.datetime.now()

    def to_dict(self):
        """ Dictionary Representation of temperature reading """
        dict = {}
        dict['id'] = self.id
        dict['home_id'] = self.home_id
        dict['device_id'] = self.device_id
        dict['ambient_temperature'] = self.ambient_temperature
        dict['ambient_humidity'] = self.ambient_humidity
        dict['outdoor_weather'] = self.outdoor_weather
        dict['atmospheric_pressure'] = self.atmospheric_pressure
        dict['timestamp'] = self.timestamp
        dict['trace_id'] = self.trace_id
        dict['date_created'] = self.date_created
    

        return dict
