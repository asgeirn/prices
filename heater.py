#!/usr/bin/env python3

import os
import requests

r = requests.get(os.environ["SWITCH_ENDPOINT"])
data = r.json()
print(data)
