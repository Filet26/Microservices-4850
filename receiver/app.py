# name: Desmond Ho
# Student ID: A01266785
# Date: 2023-09-12
# Class: ACIT 3855

import connexion
from connexion import NoContent
import json
import datetime
import os
import threading
import requests
import yaml
import logging
import logging.config
import uuid
from pykafka import KafkaClient
import time

#  constants
# MAX_EVENTS = 10
# EVENT_FILE = "events.json"


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

# make the lock
# file_lock = threading.Lock()

# with open("app_conf.yml", "r") as f:
#     app_config = yaml.safe_load(f.read())

# with open("log_conf.yml", "r") as f:
#     log_config = yaml.safe_load(f.read())
#     logging.config.dictConfig(log_config)


# logger = logging.getLogger("basicLogger")


retries = app_config["Kafka"]["retries"]
curr_retries = 0
global client
global topic
global producer
while curr_retries <= retries:
    logger.info(f"Trying to connect to Kafka, retry attempt {curr_retries}")
    try:
        client = KafkaClient(
            hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}"
        )
        topic = client.topics[str.encode(app_config["events"]["topic"])]
        producer = topic.get_sync_producer()
        logger.info("Connected to Kafka!")
        break
    except Exception as e:
        logger.error("Error connecting to Kafka: %s", e)
        curr_retries += 1
        time.sleep(app_config["Kafka"]["retry_timeout_sec"])


# functions for handling the 2 requests
def report_power_usage(body):
    # log_events(body, "power_usage")
    # url = app_config["powerusage"]["url"]
    # # url = "http://localhost:8090/usage/powerusage"
    id = uuid.uuid4()

    # # add traceID to body
    body["trace_id"] = str(id)

    # headers = {"Content-Type": "application/json"}

    logger.info(f"Received event: [power usage] request with a trace ID of {id}")

    # response = requests.post(url, json=body, headers=headers)

    # client = KafkaClient(
    #     hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}"
    # )
    # topic = client.topics[str.encode(app_config["events"]["topic"])]
    msg = {
        "type": "power_usage",
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body,
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode("utf-8"))

    logger.info(f"Returned event [power usage] response: {id} with status 201")

    return NoContent, 201


def report_temperature_reading(body):
    # url = "http://localhost:8090/usage/temperature"

    # url = app_config["temperature"]["url"]
    id = uuid.uuid4()

    # add traceID to body
    body["trace_id"] = str(id)

    # headers = {"Content-Type": "application/json"}

    logger.info(f"Received event: [temperature] request with a trace ID of {id}")

    # response = requests.post(url, json=body, headers=headers)

    # client = KafkaClient(
    #     hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}"
    # )
    # topic = client.topics[str.encode(app_config["events"]["topic"])]
    msg = {
        "type": "temperature_reading",
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body,
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode("utf-8"))

    logger.info(f"Returned event [temperature] response: {id} with status 201")

    # log_events(body, "temperature_reading")
    return NoContent, 201


def get_healthcheck():
    return NoContent, 200


# app config
app = connexion.FlaskApp(__name__, specification_dir="./")
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    app.run(port=8080, debug=True)
