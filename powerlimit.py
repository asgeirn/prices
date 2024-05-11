#!/usr/bin/env python3

import os
import datetime
import subprocess

import pandas
import requests

POWER_LIMIT_100 = int(os.getenv("POWER_LIMIT", "5000"))
POWER_LIMIT_80 = POWER_LIMIT_100 * 0.8

currentTime = datetime.datetime.utcnow()
startTime = currentTime.replace(minute=0, second=0, microsecond=0)
endTime = startTime + datetime.timedelta(hours=1)

progress = (currentTime - startTime).seconds / (endTime - startTime).seconds

tzinfo = startTime.astimezone().tzinfo

authorization = f'Bearer {os.environ["OSS_TOKEN"]}'
url = f'{os.environ["OSS_ENDPOINT"]}/{startTime.isoformat()}Z/{endTime.isoformat()}Z/1'

r = requests.get(
    url,
    headers={
        "Authorization": authorization,
        "Accept": "*/*",
        "User-Agent": "insomnia/2023.5.8",
    },
    timeout=30,
)
if r.status_code == requests.codes.ok:
    data = r.json()
    index = pandas.DatetimeIndex(data=[e["fromTime"] for e in data], tz=tzinfo)
    values = [e["activeEnergy"]["input"] for e in data]
    series = pandas.Series(index=index, data=values)
    consumption = series.sum()
    estimate = consumption / progress
    limit = consumption > POWER_LIMIT_80 or estimate > POWER_LIMIT_100
    print(
        f"{datetime.datetime.now().isoformat(sep=' ', timespec='minutes')} {consumption:.2f} (estimate {estimate:.2f}) Wh [{len(series)} items] {'!!!' if limit else ''}"
    )
    if limit:
        r = requests.put(
            f"{os.environ['SWITCH_ENDPOINT']}/state", json={"on": False}, timeout=10
        )
        if r.status_code != requests.codes.ok:
            print(r)
            subprocess.run(["./blink1-tool", "-q", "--yellow"], check=False)
        else:
            subprocess.run(["./blink1-tool", "-q", "--blue"], check=False)
else:
    print(f"{url} :: {r.status_code}")
    print(r.text)
