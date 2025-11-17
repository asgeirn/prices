#!/usr/bin/env python3

import datetime
import os
import pathlib
import subprocess

import requests


def calculate():
    try:
        override = pathlib.Path(f"{datetime.date.today()}.override")
        if override.exists():
            print(f"{datetime.datetime.now()}: Override present - turning heater ON")
            return True
        state = (
            datetime.datetime.now().minute > 0
            or datetime.datetime.now().hour not in range(6, 22)
        )
        print(f"{datetime.datetime.now()}: Turning heater {'ON' if state else 'OFF'}")
        return state
    except Exception as e:
        print(
            f"Error calculating state: {e.__class__.__name__}: {e} - turning heater ON"
        )
        return True


state = calculate()
r = requests.put(
    f"{os.environ['SWITCH_ENDPOINT']}/state", json={"on": state}, timeout=10
)
# data = r.json()
# print(data)
if r.status_code != requests.codes.ok:
    print(r)
    _ = subprocess.run(["./blink1-tool", "-q", "--yellow"], check=False)
elif state:
    _ = subprocess.run(["./blink1-tool", "-q", "--red"], check=False)
else:
    _ = subprocess.run(["./blink1-tool", "-q", "--green"], check=False)
