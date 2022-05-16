#!/usr/bin/env python3

from influxdb_client import InfluxDBClient, Point, WritePrecision

bucket = "heater"

client = InfluxDBClient.from_env_properties()

query_api = client.query_api()

query = """from(bucket: "heater")
    |> range(start: -10m)
    |> filter(fn: (r) => r._measurement == "consumption")
    |> mean()"""
tables = query_api.query(query)

for table in tables:
    for record in table.records:
        print(record)
