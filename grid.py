import os
import datetime
import requests
import pandas

def grid_fallback(day, nextday, tzinfo):
    index = pandas.DatetimeIndex(
        pandas.date_range(
            start=day, end=nextday, freq="1H", inclusive="left", tz=tzinfo
        )
    )
    data = [
        0.38,
        0.38,
        0.38,
        0.38,
        0.38,
        0.38,
        0.50,
        0.50,
        0.50,
        0.50,
        0.50,
        0.50,
        0.50,
        0.50,
        0.50,
        0.50,
        0.50,
        0.50,
        0.50,
        0.50,
        0.50,
        0.50,
        0.38,
        0.38,
    ]
    series = pandas.Series(index=index, data=data).tz_convert(tz='Europe/Oslo')
    return series


def get_grid(day, nextday, tzinfo):
    fallback = grid_fallback(day, nextday, tzinfo)
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
            return fallback
        dt = pandas.to_datetime([e["from"] for e in result], utc=True)
        index = pandas.DatetimeIndex(dt)
        series = pandas.Series(index=index, data=[e["price"] for e in result]).tz_convert(tz='Europe/Oslo')
        print(series)
        print(fallback)
        return series.combine_first(fallback)
    else:
        return fallback
