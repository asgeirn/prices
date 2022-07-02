#!/usr/bin/env python3

from influxdb_client import InfluxDBClient, Point, WritePrecision
from zoneinfo import ZoneInfo
import json
import datetime
import pandas
import pathlib

d = []

prevfile = pathlib.Path(f"{datetime.date.today() - datetime.timedelta(days=1)}.json")
if prevfile.exists():
    yesterday = json.load(open(prevfile, "rt"))
    d += yesterday

today = json.load(open(f"{datetime.date.today()}.json", "rt"))
d += today

nextfile = pathlib.Path(f"{datetime.date.today() + datetime.timedelta(days=1)}.json")
if nextfile.exists():
    tomorrow = json.load(open(nextfile, "rt"))
    d += tomorrow

index = pandas.DatetimeIndex([e["startsAt"] for e in d])
data = [e["total"] for e in d]
prices = pandas.Series(data=data, index=index)
print(prices)

bucket = "heater"
client = InfluxDBClient.from_env_properties()
query_api = client.query_api()

query = """from(bucket: "heater")
	|> range(start: -36h)
    |> filter(fn: (r) => r["_measurement"] == "consumption")
    |> filter(fn: (r) => r["_field"] == "power")
    |> window(every: 1h)
    |> integral(unit: 1m)
    |> map(fn: (r) => ({r with _value: r._value / 60.0}))
    |> duplicate(column: "_start", as: "_time")
    |> window(every: inf)"""
tables = query_api.query(query)

index = pandas.DatetimeIndex([record.get_time() for table in tables for record in table.records])
data = [record.get_value() for table in tables for record in table.records]
consumption = pandas.Series(data=data, index=index)
print(consumption)

cost = consumption.combine(prices, lambda x, y: x * y / 1000)

print(cost)

# for table in tables:
#    for record in table.records:
#        print(f"{record.get_time().astimezone(ZoneInfo('Europe/Oslo'))} {record.get_value()}")
