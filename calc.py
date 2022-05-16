#!/usr/bin/env python3

import json
import datetime
import os
import pandas
import pathlib
import requests
import subprocess

def calculate():
    try:
        d = []

        prevfile = pathlib.Path(f'{datetime.date.today() - datetime.timedelta(days=1)}.json')
        if prevfile.exists():
            yesterday = json.load(open(prevfile, 'rt'))
            d += yesterday

        today = json.load(open(f'{datetime.date.today()}.json', 'rt'))
        d += today

        nextfile = pathlib.Path(f'{datetime.date.today() + datetime.timedelta(days=1)}.json')
        if nextfile.exists():
            tomorrow = json.load(open(nextfile, 'rt'))
            d += tomorrow

        index = pandas.DatetimeIndex([e['startsAt'] for e in d])
        data = [e['total'] for e in d]
        series = pandas.Series(data=data, index=index)
        now = pandas.Timestamp.now('Europe/Oslo').replace(minute=0, second=0, microsecond=0)
        prev = now - pandas.Timedelta(hours=2)
        horizon = now + pandas.Timedelta(hours=4)
        #print(series[prev:horizon])
        current = series[now]
        future = series[prev:horizon].mean()
        state = bool(current < future)
        print(f'{datetime.datetime.now()}: {current:.4f} vs {future:.4f} - turning heater {"ON" if state else "OFF"}')
        return state
    except Exception as e:
        print(f'Error calculating state: {e} - turning heater ON')
        return True

state = calculate()
r = requests.put(f"{os.environ['SWITCH_ENDPOINT']}/state", json={'on': state})
#data = r.json()
#print(data)
if r.status_code != requests.codes.ok:
    print(r)
    subprocess.run(['./blink1-tool', '-q', '--yellow'])
elif state:
    subprocess.run(['./blink1-tool', '-q', '--red'])
else:
    subprocess.run(['./blink1-tool', '-q', '--green'])
