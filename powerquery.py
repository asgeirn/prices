#!/usr/bin/env python3

import datetime
import pathlib
import sys

import pandas
from influxdb_client import InfluxDBClient

d = []

day = datetime.date.today() - datetime.timedelta(days=1)

if len(sys.argv) > 1:
    day = datetime.date.fromisoformat(sys.argv[1])

start = datetime.datetime.combine(day, datetime.time.min)
stop = datetime.datetime.combine(day, datetime.time.max)

pricefile = pathlib.Path(f"{day}.json")
prices = pandas.read_json(path_or_buf=pricefile, orient="index", typ="series")
# print(prices)

client = InfluxDBClient.from_env_properties()
query_api = client.query_api()

query = f"""from(bucket: "heater")
    |> range(start: {start.astimezone().isoformat()}, stop: {stop.astimezone().isoformat()})
    |> filter(fn: (r) => r["_measurement"] == "consumption")
    |> filter(fn: (r) => r["_field"] == "power")
    |> window(every: 1h)
    |> integral(unit: 1m)
    |> map(fn: (r) => ({{r with _value: r._value / 60.0}}))
    |> duplicate(column: "_start", as: "_time")
    |> window(every: inf)"""

tables = query_api.query(query)


index = pandas.DatetimeIndex(
    data=[record.get_time() for table in tables for record in table.records]
)
data = [record.get_value() for table in tables for record in table.records]
consumption = pandas.Series(data=data, index=index)
# print(consumption)

cost = consumption.combine(prices, lambda x, y: x * y / 1000)

# print(cost)
print(f"{day} {cost.sum():.03f} kr, {consumption.sum() / 1000.0:.03f} kWh")

# for table in tables:
#    for record in table.records:
#        print(f"{record.get_time().astimezone(ZoneInfo('Europe/Oslo'))} {record.get_value()}")
