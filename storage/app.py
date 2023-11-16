# name: Desmond Ho
# Student ID: A01266785
# Date: 2023-09-12
# Class: ACIT 3855

import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker
from base import Base
from power_usage import PowerUsage
from temperature_reading import TemperatureReading
import json
import datetime
from threading import Thread
import yaml
import logging
import logging.config
from pykafka import KafkaClient
from pykafka.common import OffsetType
import time
import os


# DB_ENGINE = create_engine("sqlite:///readings.sqlite")

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

# with open("app_conf.yml", "r") as f:
#     app_config = yaml.safe_load(f.read())

# with open("log_conf.yml", "r") as f:
#     log_config = yaml.safe_load(f.read())
#     logging.config.dictConfig(log_config)


# logger = logging.getLogger("basicLogger")

DB_ENGINE = create_engine(
    f"mysql+pymysql://{app_config['datastore']['user']}:{app_config['datastore']['password']}@{app_config['datastore']['hostname']}:{app_config['datastore']['port']}/{app_config['datastore']['db']}"
)
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)
# increase timeout
DB_SESSION.configure(bind=DB_ENGINE, expire_on_commit=False)
logger.info(
    f"Connecting to DB. Hostname: {app_config['datastore']['hostname']} port: {app_config['datastore']['port']}"
)


# functions for handling the 2 requests
# def report_power_usage(body):
#     # log_events(body, "power_usage")

#     session = DB_SESSION()

#     pu = PowerUsage(body["home_id"],
#                     body["device_id"],
#                     body["timestamp"],
#                     body["watts"],
#                     body["voltage"],
#                     body["frequency"],
#                     body["electricity_cost_rate"],
#                     body["trace_id"])

#     session.add(pu)
#     session.commit()
#     session.close()

#     logger.debug(f"Stored Event [power usage] request with a trace id of {body['trace_id']}")

#     return NoContent, 201


# def report_temperature_reading(body):
#     # log_events(body, "temperature_reading")
#     session = DB_SESSION()


#     tr = TemperatureReading(body["home_id"],
#                             body["device_id"],
#                             body["timestamp"],
#                             body["ambient_temperature"],
#                             body["ambient_humidity"],
#                             body["outdoor_weather"],
#                             body["atmospheric_pressure"],
#                             body["trace_id"])

#     session.add(tr)
#     session.commit()
#     session.close()

#     logger.debug(f"Stored Event [temperature] request with a trace id of {body['trace_id']}")


#     return NoContent, 201


def get_power_usage(start_timestamp, end_timestamp):
    session = DB_SESSION()
    timestamp_converted = datetime.datetime.strptime(
        start_timestamp, "%Y-%m-%dT%H:%M:%SZ"
    )
    end_timestamp_converted = datetime.datetime.strptime(
        end_timestamp, "%Y-%m-%dT%H:%M:%SZ"
    )

    results = session.query(PowerUsage).filter(
        and_(
            PowerUsage.date_created >= timestamp_converted,
            PowerUsage.date_created < end_timestamp_converted,
        )
    )

    results_list = []

    for result in results:
        results_list.append(result.to_dict())

    session.close()

    logger.info(
        "Query for power usage readings after %s returns %d results",
        start_timestamp,
        len(results_list),
    )

    return results_list, 200


def get_temperature(start_timestamp, end_timestamp):
    session = DB_SESSION()
    # convert timestamp to datetime object with milliseconds
    timestamp_converted = datetime.datetime.strptime(
        start_timestamp, "%Y-%m-%dT%H:%M:%SZ"
    )
    end_timestamp_converted = datetime.datetime.strptime(
        end_timestamp, "%Y-%m-%dT%H:%M:%SZ"
    )

    results = session.query(TemperatureReading).filter(
        and_(
            TemperatureReading.date_created >= timestamp_converted,
            TemperatureReading.date_created < end_timestamp_converted,
        )
    )

    results_list = []

    for result in results:
        results_list.append(result.to_dict())

    session.close()

    logger.info(
        "Query for temperature readings after %s returns %d results",
        start_timestamp,
        len(results_list),
    )

    return results_list, 200


def process_messages():
    """Process event messages"""
    hostname = "%s:%d" % (
        app_config["events"]["hostname"],
        app_config["events"]["port"],
    )

    retries = app_config["Kafka"]["retries"]
    curr_retries = 0
    while curr_retries <= retries:
        logger.info(f"Trying to connect to Kafka, retry attempt {curr_retries}")
        try:
            client = KafkaClient(hosts=hostname)
            topic = client.topics[str.encode(app_config["events"]["topic"])]
            break
        except Exception as e:
            logger.error("Error connecting to Kafka: %s", e)
            curr_retries += 1
            time.sleep(app_config["Kafka"]["retry_timeout_sec"])

    # Create a consume on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(
        consumer_group=b"event_group",
        reset_offset_on_start=False,
        auto_offset_reset=OffsetType.LATEST,
    )
    # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode("utf-8")
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        payload = msg["payload"]
        if msg["type"] == "power_usage":  # Change this to your event type
            # Store the event1 (i.e., the payload) to the DB

            session = DB_SESSION()

            pu = PowerUsage(
                payload["home_id"],
                payload["device_id"],
                payload["timestamp"],
                payload["watts"],
                payload["voltage"],
                payload["frequency"],
                payload["electricity_cost_rate"],
                payload["trace_id"],
            )

            session.add(pu)
            session.commit()
            session.close()

            logger.debug(
                f"Stored Event [power usage] request with a trace id of {payload['trace_id']}"
            )

        elif msg["type"] == "temperature_reading":  # Change this to your event type
            # Store the event2 (i.e., the payload) to the DB

            session = DB_SESSION()

            tr = TemperatureReading(
                payload["home_id"],
                payload["device_id"],
                payload["timestamp"],
                payload["ambient_temperature"],
                payload["ambient_humidity"],
                payload["outdoor_weather"],
                payload["atmospheric_pressure"],
                payload["trace_id"],
            )

            session.add(tr)
            session.commit()
            session.close()

            logger.debug(
                f"Stored Event [temperature] request with a trace id of {payload['trace_id']}"
            )
        else:
            logger.error("Unexpected event type: %s" % msg["type"])
        # Commit the new message as being read
        consumer.commit_offsets()


def get_healthcheck():
    return NoContent, 200


# app config
app = connexion.FlaskApp(__name__, specification_dir="./")
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.daemon = True
    t1.start()

    app.run(port=8090)
