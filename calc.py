#!/usr/bin/env python3

import datetime
import os
import pathlib
import subprocess

import pandas
import requests

def calculate():
    try:
        files = [
            f"{datetime.date.today() - datetime.timedelta(days=1)}.json",
            f"{datetime.date.today()}.json",
            f"{datetime.date.today() + datetime.timedelta(days=1)}.json",
        ]
        paths = [pathlib.Path(it) for it in files]
        inputs = [
            pandas.read_json(path_or_buf=p, orient="index", typ="series")
            for p in paths
            if p.exists()
        ]
        series = pandas.concat(inputs)
        now = pandas.Timestamp.now("Europe/Oslo").replace(
            minute=0, second=0, microsecond=0
        )
        prev = now - pandas.Timedelta(hours=2)
        next = now + pandas.Timedelta(hours=3)
        current = series[now]
        short = series[prev:next].mean()
        state = bool(current < short)
        print(
            f'{datetime.datetime.now()}: {current:.4f} vs {short:.4f} - turning {"ON" if state else "OFF"}'
        )
        return state
    except Exception as e:
        print(f"Error calculating state: {e} - turning heater ON")
        return True


override = pathlib.Path('./override')
state = override.exists() or calculate()
r = requests.put(f"{os.environ['SWITCH_ENDPOINT']}/state", json={"on": state}, timeout=10)
# data = r.json()
# print(data)
if r.status_code != requests.codes.ok:
    print(r)
    subprocess.run(["./blink1-tool", "-q", "--yellow"], check=False)
elif state:
    subprocess.run(["./blink1-tool", "-q", "--red"], check=False)
else:
    subprocess.run(["./blink1-tool", "-q", "--green"], check=False)
