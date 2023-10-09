#!/usr/bin/env python3

import datetime
import os
import pathlib

import numpy
import pandas
import requests

from grid import get_grid

def get_power():
    authorization = f'Bearer {os.environ["TIBBER_TOKEN"]}'
    query = """
{
  viewer {
    homes {
			currentSubscription {
				priceInfo {
					range(resolution: HOURLY, last: 48) {
						nodes {
							total
							startsAt
						}
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
    result = data["data"]["viewer"]["homes"][0]["currentSubscription"]["priceInfo"]["range"]["nodes"]
    tzinfo = datetime.datetime.now().astimezone().tzinfo
    index = pandas.DatetimeIndex([e["startsAt"] for e in result], tz="UTC").tz_convert(
        tzinfo
    )
    series = pandas.Series(index=index, data=[e["total"] for e in result])
    return series

yesterday = datetime.date.today() - datetime.timedelta(days=1)
p = pathlib.Path(f"{yesterday}.json")

def addfloat(x, y):
    if not isinstance(x, numpy.float64):
        raise Exception(f"{x} is not numeric")
    if not isinstance(y, numpy.float64):
        raise Exception(f"{y} is not numeric")
    return x + y

if not p.is_file():
    tzinfo = datetime.datetime.now().astimezone().tzinfo
    day = datetime.date.today() - datetime.timedelta(days=1)
    nextday = day+datetime.timedelta(days=1)
    start = pandas.Timestamp.today(tz=tzinfo).normalize()
    end = start - pandas.Timedelta(1, 'hour')
    start = start - pandas.Timedelta(1, 'day')
    power = get_power()[start : end]
    grid = get_grid(day, nextday, tzinfo)
    cost = power.combine(grid, addfloat)
    print(cost)
    cost.to_json(path_or_buf=p, date_format="iso")
