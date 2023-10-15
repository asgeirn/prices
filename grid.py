import os
import datetime
import requests
import pandas

def grid_fallback(day, nextday, tzinfo):
    print(f"{datetime.datetime.now()}: Using fallback for nettleie - you should check that they are correct!")
    index = pandas.DatetimeIndex(pandas.date_range(start=day, end=nextday, freq='1H', inclusive='left', tz=tzinfo))
    data = [ 0.38, 0.38, 0.38, 0.38, 0.38, 0.38, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.38, 0.38 ]
    series = pandas.Series(index=index, data=data)
    return series

def get_grid(day, nextday, tzinfo):
    apiToken = os.environ["GRID_TOKEN"]
    baseUri = os.environ["GRID_URI"]
    tariffKey = os.environ["GRID_TARIFF_KEY"]
    url = f"{baseUri}/api/1.0/tariffquery"
    print(f"{datetime.datetime.now()}: Fetching {url} ... ", end="", flush=True)
    r = requests.get(
        url,
        params={
            "TariffKey": tariffKey,
            "StartTime": f"{day.isoformat()}T00:00:00Z",
            "EndTime": f"{nextday.isoformat()}T00:00:00Z",
        },
        headers={"X-API-Key": apiToken},
    )
    print(f"{r.status_code}")
    if r.status_code == 200:
        data = r.json()
        result = [
            {"from": it["startTime"], "price": it["energyPrice"]["total"]}
            for it in data["gridTariff"]["tariffPrice"]["hours"]
        ]
        if len(result) == 0:
            return grid_fallback(day, nextday, tzinfo)
        index = pandas.DatetimeIndex([e["from"] for e in result], tz="UTC").tz_convert(
            tzinfo
        )
        series = pandas.Series(index=index, data=[e["price"] for e in result])
        return series
    else:
        return grid_fallback(day, nextday, tzinfo)
