#!/usr/bin/env python3

import sys
import json
import pathlib
import pandas

for f in sys.argv[1:]:
    print(f)
    todayfile = pathlib.Path(f)
    d = json.load(open(todayfile, "rt"))
    index = pandas.DatetimeIndex([e["startsAt"] for e in d])
    data = [e["total"] for e in d]
    series = pandas.Series(data=data, index=index)
    out = pathlib.Path(todayfile.name)
    series.to_json(path_or_buf=out, date_format="iso", indent=2)
