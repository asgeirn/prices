#!/usr/bin/env python3

import os
import requests
import datetime
import json
import pathlib

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

tomorrow = f"{datetime.date.today() + datetime.timedelta(days=1)}"
url = "https://api.tibber.com/v1-beta/gql"
p = pathlib.Path(f"{tomorrow}.json")


def nettleie(it):
    dt = datetime.datetime.fromisoformat(it["startsAt"])
    if dt.hour in range(6, 22):
        it["total"] = float(it["total"]) + 0.4725
    else:
        it["total"] = float(it["total"]) + 0.3525
    return it


if not p.is_file():
    print(f"{datetime.datetime.now()}: Fetching {url} ... ", end="")
    r = requests.post(
        url, data={"query": query}, headers={"Authorization": authorization}
    )
    print(f"{r.status_code}")
    if r.status_code == requests.codes.ok:
        data = r.json()
        result = data["data"]["viewer"]["homes"][0]["currentSubscription"]["priceInfo"][
            "tomorrow"
        ]
        if result:
            json.dump([nettleie(it) for it in result], open(p, "wt"))
        else:
            print(json.dumps(data))
