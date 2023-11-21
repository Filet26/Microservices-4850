# name: Desmond Ho
# Student ID: A01266785
# Date: 2023-09-12
# Class: ACIT 3855

import connexion
from connexion import NoContent

# from power_usage import PowerUsage
# from temperature_reading import TemperatureReading
import json
import datetime
import os
import yaml
import logging
import logging.config
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from flask_cors import CORS, cross_origin


if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(app_conf_file, "r") as f:
    app_config = yaml.safe_load(f.read())
# External Logging Configuration
with open(log_conf_file, "r") as f:
    log_config = yaml.safe_load(f.read())

logging.config.dictConfig(log_config)
logger = logging.getLogger("basicLogger")
logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)


# DB_ENGINE = create_engine("sqlite:///readings.sqlite")


# with open("app_conf.yml", "r") as f:
#     app_config = yaml.safe_load(f.read())

# with open("log_conf.yml", "r") as f:
#     log_config = yaml.safe_load(f.read())
#     logging.config.dictConfig(log_config)


# logger = logging.getLogger("basicLogger")

# DB_ENGINE = create_engine(f"mysql+pymysql://{app_config['datastore']['user']}:{app_config['datastore']['password']}@{app_config['datastore']['hostname']}:{app_config['datastore']['port']}/{app_config['datastore']['db']}")
# Base.metadata.bind = DB_ENGINE
# DB_SESSION = sessionmaker(bind=DB_ENGINE)


def get_event_stats():
    logger.info("Request has started")
    #  read current stats from data.json, create if not exist
    try:
        with open(app_config["datastore"]["filename"], "r+") as f:
            stats = json.loads(f.read())
    except:
        with open("/data/data.json", "w") as f:
            f.write("{}")
        logger.error("Statistics do not exist")
        return NoContent, 404

    #  convert stats to dict
    stats = dict(stats)

    logger.debug("Statistics: %s", stats)

    logger.info("Request has completed")

    return stats, 200


def write_to_file(power_usage_data, temperature_data, now):
    # Open file and get current stats
    with open(app_config["datastore"]["filename"], "r+") as f:
        stats = json.loads(f.read())

    # Get the number of readings from the file
    num_powerusage_readings = stats["num_powerusage_readings"]
    num_temperature_readings = stats["num_temperature_readings"]
    max_watts_reading = stats["max_watts_reading"]
    max_temperature_reading = stats["max_temperature_reading"]
    last_updated = stats["last_updated"]

    dict = {
        "num_powerusage_readings": num_powerusage_readings,
        "num_temperature_readings": num_temperature_readings,
        "max_watts_reading": max_watts_reading,
        "max_temperature_reading": max_temperature_reading,
        "last_updated": last_updated,
    }

    # Update power usage data if available
    if len(power_usage_data.json()) > 0:
        dict["num_powerusage_readings"] += len(power_usage_data.json())
        max_power_reading = max(power_usage_data.json(), key=lambda x: x["watts"])[
            "watts"
        ]
        dict["max_watts_reading"] = max(max_power_reading, max_watts_reading)

    # Update temperature data if available
    if len(temperature_data.json()) > 0:
        dict["num_temperature_readings"] += len(temperature_data.json())
        max_temp_reading = max(
            temperature_data.json(), key=lambda x: x["ambient_temperature"]
        )["ambient_temperature"]
        dict["max_temperature_reading"] = max(max_temp_reading, max_temperature_reading)

    dict["last_updated"] = now

    json_convert = json.dumps(dict, indent=4)

    with open(app_config["datastore"]["filename"], "w") as f:
        f.write(json_convert)

    logger.debug("Writing to file - Updated data: %s", json_convert)

    logger.info("Periodic Processing has Ended")


def populate_stats():
    logger.info("Start Periodic Processing")
    #  read current stats from data.json, create if not exist
    try:
        with open(app_config["datastore"]["filename"], "r+") as f:
            # if empty, create default stats
            if os.stat(app_config["datastore"]["filename"]).st_size <= 4:
                stats = {
                    "num_powerusage_readings": 0,
                    "max_watts_reading": 0,
                    "num_temperature_readings": 0,
                    "max_temperature_reading": 0,
                    "last_updated": "2021-02-05T12:39:16Z",
                }
                f.write(json.dumps(stats))
                return
            else:
                stats = json.loads(f.read())
    except:
        with open("/data/data.json", "w") as f:
            stats = {
                "num_powerusage_readings": 0,
                "max_watts_reading": 0,
                "num_temperature_readings": 0,
                "max_temperature_reading": 0,
                "last_updated": "2021-02-05T12:39:16Z",
            }
            f.write(json.dumps(stats))
            # default stats

    #  get current date time
    now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    # get last created date time, convert to datetime object
    last_updated = stats["last_updated"]
    # headers
    headers = {"Content-Type": "application/json"}

    #  get power usage stats
    power_usage_params = {"timestamp": last_updated}

    power_usage_data = requests.get(
        app_config["eventstore"]["url"]
        + "/usage/powerusagedata?start_timestamp="
        + last_updated
        + "&end_timestamp="
        + now,
        headers=headers,
    )
    logger.info("Number of events from power usage: %s", len(power_usage_data.json()))

    #  log error if not 200
    if power_usage_data.status_code != 200:
        logger.error("Error, did not receive 200 status code from power usage")

    #  get temperature stats
    temperature_params = {"timestamp": last_updated}

    temperature_data = requests.get(
        app_config["eventstore"]["url"]
        + "/usage/temperaturedata?start_timestamp="
        + last_updated
        + "&end_timestamp="
        + now,
        headers=headers,
    )
    logger.info("Number of events from temperature: %s", len(temperature_data.json()))

    # log error
    if temperature_data.status_code != 200:
        logger.error(
            f"Error, did not receive 200 status code from temperature, got {temperature_data.status_code}"
        )

    #  write new data to file
    write_to_file(power_usage_data, temperature_data, now)


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(
        populate_stats, "interval", seconds=app_config["scheduler"]["period_sec"]
    )
    sched.start()


def get_healthcheck():
    return NoContent, 200


# app config
app = connexion.FlaskApp(__name__, specification_dir="./")
app.add_api(
    "openapi.yaml",
    base_path="/processing",
    strict_validation=True,
    validate_responses=True,
)

if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config["CORS_HEADERS"] = "Content-Type"


if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100)
