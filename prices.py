#!/usr/bin/env python3

import datetime
import pathlib
import sys

import numpy
import pandas
import requests

from grid import get_grid


def get_power(date: datetime.date):
    url = f"https://www.hvakosterstrommen.no/api/v1/prices/{date.strftime('%Y/%m-%d')}_NO1.json"
    print(f"{datetime.datetime.now()}: Fetching {url} ... ", end="", flush=True)
    r = requests.get(url, timeout=60)
    print(f"{r.status_code}")
    r.raise_for_status()
    result = r.json()
    dt = pandas.to_datetime([e["time_start"] for e in result], utc=True)
    index = pandas.DatetimeIndex(dt)
    series = pandas.Series(
        index=index, data=[e["NOK_per_kWh"] * 1.25 for e in result]
    ).tz_convert(tz="Europe/Oslo")
    return series


def addfloat(x, y):
    if not isinstance(x, numpy.float64):
        print(f"x={x} is not numeric, price will be wrong!")
        return y
    if not isinstance(y, numpy.float64):
        print(f"y={y} is not numeric, price will be wrong!")
        return x
    return x + y


day = datetime.date.today() + datetime.timedelta(days=1)
if len(sys.argv) > 1:
    if sys.argv[1] == "--today":
        day = datetime.date.today()
    elif sys.argv[1] == "--yesterday":
        day = datetime.date.today() - datetime.timedelta(days=1)
p = pathlib.Path(f"{day}.json")

if not p.is_file():
    nextday = day + datetime.timedelta(days=1)
    power = get_power(day)
    grid = get_grid(day, nextday)
    cost = power.combine(grid, addfloat)
    cost.to_json(path_or_buf=p, date_format="iso")
