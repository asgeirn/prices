#!/usr/bin/env python3

import os
import requests
from influxdb_client import Point, InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

r = requests.get(os.environ["SENSOR_ENDPOINT"], timeout=10)
r.raise_for_status()
data = r.json()
state = data["state"]

current = state["current"]
power = state["power"]
voltage = state["voltage"]

BUCKET = "heater"

client = InfluxDBClient.from_env_properties()
write_api = client.write_api(write_options=SYNCHRONOUS)

point = (
    Point("consumption")
    .field("power", power)
    .field("current", current)
    .field("voltage", voltage)
)
write_api.write(bucket=BUCKET, record=point)
