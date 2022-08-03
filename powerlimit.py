#!/usr/bin/env python3

import requests
import os
import datetime
import pandas
import subprocess

startTime = datetime.datetime.utcnow().replace(minute=0, second=0, microsecond=0)
endTime = startTime + datetime.timedelta(hours=1)

tzinfo = startTime.astimezone().tzinfo

authorization = f'Bearer {os.environ["OSS_TOKEN"]}'
url = f'{os.environ["OSS_ENDPOINT"]}/{startTime.isoformat()}Z/{endTime.isoformat()}Z/Minute'

r = requests.get(url, headers={"Authorization": authorization})
print(f"{url} :: {r.status_code}")
if r.status_code == requests.codes.ok:
    data = r.json()
    index = pandas.DatetimeIndex(data=[e["fromTime"] for e in data], tz=tzinfo)
    values = [e["activeEnergy"]["input"] for e in data]
    series = pandas.Series(index=index, data=values)
    consumption = series.sum()
    print(f"{consumption:.2f} kWh")
    if consumption > 4000.0:
        print("Now at 80 percent limit!")
        r = requests.put(f"{os.environ['SWITCH_ENDPOINT']}/state", json={"on": False})
        if r.status_code != requests.codes.ok:
            print(r)
            subprocess.run(["./blink1-tool", "-q", "--yellow"])
        else:
            subprocess.run(["./blink1-tool", "-q", "--blue"])
