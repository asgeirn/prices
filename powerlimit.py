#!/usr/bin/env python3

import requests
import os
import datetime
import pandas
import subprocess

currentTime = datetime.datetime.utcnow()
startTime = currentTime.replace(minute=0, second=0, microsecond=0)
endTime = startTime + datetime.timedelta(hours=1)

progress = (currentTime - startTime).seconds / (endTime - startTime).seconds

tzinfo = startTime.astimezone().tzinfo

authorization = f'Bearer {os.environ["OSS_TOKEN"]}'
url = f'{os.environ["OSS_ENDPOINT"]}/{startTime.isoformat()}Z/{endTime.isoformat()}Z/Minute'

r = requests.get(url, headers={"Authorization": authorization})
# print(f"{url} :: {r.status_code}")
if r.status_code == requests.codes.ok:
    data = r.json()
    index = pandas.DatetimeIndex(data=[e["fromTime"] for e in data], tz=tzinfo)
    values = [e["activeEnergy"]["input"] for e in data]
    series = pandas.Series(index=index, data=values)
    consumption = series.sum()
    estimate = consumption / progress
    limit = consumption > 8000.0 or estimate > 9000.0
    print(
        f"{datetime.datetime.now().isoformat(sep=' ', timespec='minutes')} {consumption:.2f} (estimate {estimate:.2f}) Wh [{len(series)} items] {'!!!' if limit else ''}"
    )
    if limit:
        r = requests.put(f"{os.environ['SWITCH_ENDPOINT']}/state", json={"on": False})
        if r.status_code != requests.codes.ok:
            print(r)
            subprocess.run(["./blink1-tool", "-q", "--yellow"])
        else:
            subprocess.run(["./blink1-tool", "-q", "--blue"])
