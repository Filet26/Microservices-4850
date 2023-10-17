import sqlite3

conn = sqlite3.connect('readings.sqlite')

c = conn.cursor()
c.execute('''
          CREATE TABLE power_usage
          (id INTEGER PRIMARY KEY ASC, 
          home_id VARCHAR(250) NOT NULL,
           device_id VARCHAR(250) NOT NULL,
           watts INTEGER NOT NULL,
           voltage INTEGER NOT NULL,
           frequency INTEGER NOT NULL,
           electricity_cost_rate FLOAT NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
          trace_id VARCHAR(250) NOT NULL,
           date_created VARCHAR(100) NOT NULL)
          ''')

c.execute('''
          CREATE TABLE temperature_readings
          (id INTEGER PRIMARY KEY ASC, 
           home_id VARCHAR(250) NOT NULL,
           device_id VARCHAR(250) NOT NULL,
           ambient_temperature FLOAT NOT NULL,
          ambient_humidity FLOAT NOT NULL,
          outdoor_weather VARCHAR(250) NOT NULL,
          atmospheric_pressure FLOAT NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
            trace_id VARCHAR(250) NOT NULL,
           date_created VARCHAR(100) NOT NULL)
          ''')

conn.commit()
conn.close()
