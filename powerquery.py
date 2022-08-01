#!/usr/bin/env python3

import datetime
import json
import pathlib

import pandas
from influxdb_client import InfluxDBClient

d = []

tzinfo = datetime.datetime.now().astimezone().tzinfo
start = datetime.datetime.combine(datetime.date.today(), datetime.time.min)

prevfile = pathlib.Path(f"{datetime.date.today() - datetime.timedelta(days=1)}.json")
if prevfile.exists():
    yesterday = json.load(open(prevfile, "rt"))
    d += yesterday
    start -= datetime.timedelta(days=1)

today = json.load(open(f"{datetime.date.today()}.json", "rt"))
d += today

nextfile = pathlib.Path(f"{datetime.date.today() + datetime.timedelta(days=1)}.json")
if nextfile.exists():
    tomorrow = json.load(open(nextfile, "rt"))
    d += tomorrow

index = pandas.DatetimeIndex(data=[e["startsAt"] for e in d], tz=tzinfo)
data = [e["total"] for e in d]
prices = pandas.Series(data=data, index=index)
print(prices)

client = InfluxDBClient.from_env_properties()
query_api = client.query_api()

query = f"""from(bucket: "heater")
    |> range(start: {start.astimezone().isoformat()})
    |> filter(fn: (r) => r["_measurement"] == "consumption")
    |> filter(fn: (r) => r["_field"] == "power")
    |> window(every: 1h)
    |> integral(unit: 1m)
    |> map(fn: (r) => ({{r with _value: r._value / 60.0}}))
    |> duplicate(column: "_start", as: "_time")
    |> window(every: inf)"""

tables = query_api.query(query)


index = pandas.DatetimeIndex(data=[record.get_time() for table in tables for record in table.records], tz=tzinfo)
data = [record.get_value() for table in tables for record in table.records]
consumption = pandas.Series(data=data, index=index)
print(consumption)

cost = consumption.combine(prices, lambda x, y: x * y / 1000)

print(cost)
print(cost.sum())

# for table in tables:
#    for record in table.records:
#        print(f"{record.get_time().astimezone(ZoneInfo('Europe/Oslo'))} {record.get_value()}")
