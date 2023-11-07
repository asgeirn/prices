#!/usr/bin/env python3

import os
import requests

r = requests.get(os.environ["SWITCH_ENDPOINT"], timeout=10)
data = r.json()
print(data)
