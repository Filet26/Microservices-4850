from sqlalchemy import Column, Integer, String, DateTime, Float
from base import Base
import datetime


class PowerUsage(Base):

    __tablename__ = "power_usage"

    id = Column(Integer, primary_key=True)
    home_id = Column(String(250), nullable=False)
    device_id = Column(String(250), nullable=False)
    watts = Column(Integer, nullable=False)
    voltage = Column(Integer, nullable=False)
    frequency = Column(Integer, nullable=False)
    electricity_cost_rate = Column(Float, nullable=False)
    timestamp = Column(String(100), nullable=False)
    trace_id = Column(String(250), nullable=False)
    date_created = Column(DateTime, nullable=False)
    

    def __init__(self, home_id, device_id, timestamp, watts, voltage, frequency, electricity_cost_rate, trace_id):
        """ Initializes a blood pressure reading """
        self.home_id = home_id
        self.device_id = device_id
        self.watts = watts
        self.voltage = voltage
        self.frequency = frequency
        self.electricity_cost_rate = electricity_cost_rate
        self.timestamp = timestamp
        self.trace_id = trace_id
        self.date_created = datetime.datetime.now()

    def to_dict(self):
        """ Dictionary Representation of power usage """
        dict = {}
        dict['id'] = self.id
        dict['home_id'] = self.home_id
        dict['device_id'] = self.device_id
        dict['watts'] = self.watts
        dict['voltage'] = self.voltage
        dict['frequency'] = self.frequency
        dict['electricity_cost_rate'] = self.electricity_cost_rate
        dict['timestamp'] = self.timestamp
        dict['trace_id'] = self.trace_id
        dict['date_created'] = self.date_created

        return dict
