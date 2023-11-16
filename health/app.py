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
    logger.info("Polling health check status")
    # get the current timestamp
    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    #  send request to all urls, and record the response, if no response after 5 seconds
    # for service in app_config["services"]:
    #     url = app_config["services"][service]["url"] + "/usage/health"
    #     try:
    #         r = requests.get(url, timeout=5)
    #         if r.status_code == 200:
    #             logger.info("%s health check passed" % service)
    #             app_config["services"][service]["status"] = "pass"
    #             app_config["services"][service]["last_check"] = now
    #         else:
    #             logger.error("%s health check failed" % service)
    #             app_config["services"][service]["status"] = "fail"
    #             app_config["services"][service]["last_check"] = now
    #     except requests.exceptions.RequestException as e:
    #         logger.error("%s health check timed out" % service)
    #         app_config["services"][service]["status"] = "timeout"
    #         app_config["services"][service]["last_check"] = now

    for service in app_config["endpoints"]:
        print(app_config["endpoints"][service]["url"])


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(
        get_health_status, "interval", seconds=app_config["scheduler"]["period_sec"]
    )
    sched.start()


def get_heathcheck():
    return NoContent, 200


# app config
app = connexion.FlaskApp(__name__, specification_dir="./")
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)
CORS(app.app)
app.app.config["CORS_HEADERS"] = "Content-Type"


if __name__ == "__main__":
    init_scheduler()
    app.run(port=8120)
