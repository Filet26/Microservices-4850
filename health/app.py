# name: Desmond Ho
# Student ID: A01266785
# Date: 2023-11-15
# Class: ACIT 3855

import connexion
from connexion import NoContent
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


def get_health_status():
    logger.info("Received Get request for all service status")
    try:
        with open(app_config["datastore"]["filename"], "r") as f:
            health_status_dict = json.loads(f.read())

            return health_status_dict, 200
    except:
        health_status_dict = {
            "receiver": "",
            "storage": "",
            "processing": "",
            "audit": "",
            "last_updated": "",
        }
        return health_status_dict, 200


def update_health_status():
    logger.info("Polling health check status")
    # get the current timestamp
    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    # open the file in write mode, if it doesn't exist, create a new one
    try:
        with open(app_config["datastore"]["filename"], "r+") as f:
            health_status_dict = json.loads(f.read())
    except:
        health_status_dict = {
            "receiver": "",
            "storage": "",
            "processing": "",
            "audit": "",
            "last_updated": "",
        }
        with open(app_config["datastore"]["filename"], "w") as f:
            f.write(json.dumps(health_status_dict))

    for service in app_config["endpoints"]:
        url = app_config["endpoints"][service]["url"] + "/usage/health"
        # print("URL ==============================", url)
        logger.info("Sending health check request to %s" % url)
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                # print("Health check passed")
                health_status_dict[service] = "Running"
            else:
                health_status_dict[service] = "Down"
        except:
            # print("Health check timed out")
            health_status_dict[service] = "Down"

    health_status_dict["last_updated"] = now

    with open(app_config["datastore"]["filename"], "w") as f:
        f.write(json.dumps(health_status_dict))


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(
        update_health_status, "interval", seconds=app_config["scheduler"]["period_sec"]
    )
    sched.start()


def get_heathcheck():
    return NoContent, 200


# app config
app = connexion.FlaskApp(__name__, specification_dir="./")
app.add_api(
    "openapi.yaml", base_path="/health", strict_validation=True, validate_responses=True
)
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config["CORS_HEADERS"] = "Content-Type"


if __name__ == "__main__":
    init_scheduler()
    app.run(port=8120)
