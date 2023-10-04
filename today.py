#!/usr/bin/env python3

import datetime
import os
import pathlib

import numpy
import pandas
import requests


def get_power():
    authorization = f'Bearer {os.environ["TIBBER_TOKEN"]}'
    query = """
  {
    viewer {
      homes {
        currentSubscription{
          priceInfo{
            today {
              total
              startsAt
            }
          }
        }
      }
    }
  }
  """
    url = "https://api.tibber.com/v1-beta/gql"
    print(f"{datetime.datetime.now()}: Fetching {url} ... ", end="", flush=True)
    r = requests.post(
        url, data={"query": query}, headers={"Authorization": authorization}
    )
    print(f"{r.status_code}")
    r.raise_for_status()
    data = r.json()
    result = data["data"]["viewer"]["homes"][0]["currentSubscription"]["priceInfo"][
        "today"
    ]
    tzinfo = datetime.datetime.now().astimezone().tzinfo
    index = pandas.DatetimeIndex([e["startsAt"] for e in result], tz="UTC").tz_convert(
        tzinfo
    )
    series = pandas.Series(index=index, data=[e["total"] for e in result])
    return series


def get_grid():
    tzinfo = datetime.datetime.now().astimezone().tzinfo
    day = datetime.date.today()
    nextday = day+datetime.timedelta(days=1)

    apiToken = os.environ["GRID_TOKEN"]
    baseUri = os.environ["GRID_URI"]
    tariffKey = os.environ["GRID_TARIFF_KEY"]
    url = f"{baseUri}/api/1.0/tariffquery"
    print(f"{datetime.datetime.now()}: Fetching {url} ... ", end="", flush=True)
    r = requests.get(
        url,
        params={
            "TariffKey": tariffKey,
            "StartTime": f"{day.isoformat()}T00:00:00Z",
            "EndTime": f"{nextday.isoformat()}T00:00:00Z",
        },
        headers={"X-API-Key": apiToken},
    )
    print(f"{r.status_code}")
    if r.status_code == 200:
        data = r.json()
        result = [
            {"from": it["startTime"], "price": it["energyPrice"]["total"]}
            for it in data["gridTariff"]["tariffPrice"]["hours"]
        ]
        index = pandas.DatetimeIndex([e["from"] for e in result], tz="UTC").tz_convert(
            tzinfo
        )
        series = pandas.Series(index=index, data=[e["price"] for e in result])
        return series
    else:
        print("Using fallback for nettleie - you should check that they are correct!")
        index = pandas.DatetimeIndex(pandas.date_range(start=day, end=nextday, freq='1H', inclusive='left', tz=tzinfo))
        data = [ 0.35, 0.35, 0.35, 0.35, 0.35, 0.35, 0.47, 0.47, 0.47, 0.47, 0.47, 0.47, 0.47, 0.47, 0.47, 0.47, 0.47, 0.47, 0.47, 0.47, 0.47, 0.47, 0.35, 0.35 ]
        series = pandas.Series(index=index, data=data)
        return series

today = f"{datetime.date.today()}"
p = pathlib.Path(f"{today}.json")

def addfloat(x, y):
    if not isinstance(x, numpy.float64):
        return y
    if not isinstance(y, numpy.float64):
        return x
    return x + y

if not p.is_file():
    power = get_power()
    grid = get_grid()
    cost = power.combine(grid, addfloat).drop_duplicates()
    print(cost)
    cost.to_json(path_or_buf=p, date_format="iso")
