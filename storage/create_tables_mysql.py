import mysql.connector

db_conn = mysql.connector.connect(
    host="kafkaprod1.westus3.cloudapp.azure.com",
    user="root",
    password="BurgerCheese3344",
    database="events"
)

db_cursor = db_conn.cursor()

db_cursor.execute('''
    CREATE TABLE power_usage (
        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        home_id VARCHAR(250) NOT NULL,
        device_id VARCHAR(250) NOT NULL,
        watts INTEGER NOT NULL,
        voltage INTEGER NOT NULL,
        frequency INTEGER NOT NULL,
        electricity_cost_rate FLOAT NOT NULL,
        timestamp VARCHAR(100) NOT NULL,
        trace_id VARCHAR(250) NOT NULL,
        date_created VARCHAR(100) NOT NULL
    )
''')

db_cursor.execute('''
    CREATE TABLE temperature_readings (
        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        home_id VARCHAR(250) NOT NULL,
        device_id VARCHAR(250) NOT NULL,
        ambient_temperature FLOAT NOT NULL,
        ambient_humidity FLOAT NOT NULL,
        outdoor_weather VARCHAR(250) NOT NULL,
        atmospheric_pressure FLOAT NOT NULL,
        timestamp VARCHAR(100) NOT NULL,
        trace_id VARCHAR(250) NOT NULL,
        date_created VARCHAR(100) NOT NULL
    )
''')

db_conn.commit()
db_conn.close()
