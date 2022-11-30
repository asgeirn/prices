#!/usr/bin/env python3

import datetime
import os
import pathlib

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
            tomorrow {
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
        "tomorrow"
    ]
    tzinfo = datetime.datetime.now().astimezone().tzinfo
    index = pandas.DatetimeIndex([e["startsAt"] for e in result], tz="UTC").tz_convert(
        tzinfo
    )
    series = pandas.Series(index=index, data=[e["total"] for e in result])
    return series


def get_grid():
    tzinfo = datetime.datetime.now().astimezone().tzinfo
    day = datetime.date.today() + datetime.timedelta(days=1)

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
            "EndTime": f"{(day+datetime.timedelta(days=1)).isoformat()}T00:00:00Z",
        },
        headers={"X-API-Key": apiToken},
    )
    print(f"{r.status_code}")
    r.raise_for_status()
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


tomorrow = f"{datetime.date.today() + datetime.timedelta(days=1)}"
p = pathlib.Path(f"{tomorrow}.json")

if not p.is_file():
    grid = get_grid()
    power = get_power()
    cost = power.combine(grid, lambda x, y: x + y)
    cost.to_json(path_or_buf=p, date_format="iso", indent=2)
