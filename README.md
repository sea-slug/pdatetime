# pdatetime

異世界ピスカで使われる時間，時刻を扱うためのライブラリです．

# DEMO

```
>>> import pdatetime
>>> x = pdatetime.pdatetime.now()
>>> print(x)
424/7/01[1] 00:73:03
>>> f3 = pdatetime.ptimedelta(fejs=3)
>>> print(f3)
0 gaja, 03:00:00
>>> print(x+f3)
424/7/01[1] 03:73:03
```

# Features

- show various format
```
>>> x.strftime()
'424/7/01[1] 00:73:03'
>>> x.strftime("%d%m%g_%f%q%s")
'424701_007303'
```

- compliant with "datetime"
```
>>> datetime.datetime(year=2023, month=12, day=1)
datetime.datetime(2023, 12, 1, 0, 0)
```
```
>>> pdatetime.pdatetime(dizi=424, moje=7, gaja=1)
pdatetime(dizi=424, moje=7, gaja=1)
```

# Requirement

- Python 3.x

# Installation

- With pip:
```
pip install git+https://github.com/sea-slug/pdatetime
```