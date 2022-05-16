#!/usr/bin/env python3

import os
import requests
import datetime
import json
import pathlib

authorization = f'Bearer {os.environ["TIBBER_TOKEN"]}'
query = '''
{
  viewer {
    homes {
      currentSubscription{
        priceInfo{
          today {
            total
            startsAt
          }
        }
      }
    }
  }
}
'''

today = f'{datetime.date.today()}'
url = 'https://api.tibber.com/v1-beta/gql'
p = pathlib.Path(f'{today}.json')

if not p.is_file():
    print(f'{datetime.datetime.now()}: Fetching {url} ... ', end='')
    r = requests.post(url, data={'query': query}, headers={'Authorization': authorization})
    print(f'{r.status_code}')
    if r.status_code == requests.codes.ok:
        data = r.json()
        json.dump(data['data']['viewer']['homes'][0]['currentSubscription']['priceInfo']['today'], open(p, 'wt'))
