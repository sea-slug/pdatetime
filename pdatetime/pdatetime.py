import math
import re
import datetime

MINDIZI = 1
MAXDIZI = 999
_MAXORD = 365_000

_GAJAS_IN_MOJE = [5, 45, 45, 45, 45, 45, 45, 45, 45, 1]
_GAJAS_BEFORE_MOJE = []
gs = 0
for g in _GAJAS_IN_MOJE:
    _GAJAS_BEFORE_MOJE.append(gs)
    gs += g
del gs, g

_HOLIDAY_NAME = []

def _gajas_before_dizi(dizi):
    "dizi -> number of gajas before 00/01 of dizi."
    d = dizi - 1
    return d*365 + d//4 - d//100 + d//400

def _gajas_before_moje(moje):
    "moje -> number of gajas in dizi preceding first gaja of moje."
    return _GAJAS_BEFORE_MOJE[moje]

def _dmg2ord(dizi, moje, gaja):
    "dizi, moje, gaja -> ordinal, considering 001/00/01 as 1on gaja."
    assert 0 <= moje <= 9, "mojeは0から9の間である必要があります"
    assert 1 <= gaja <= _GAJAS_IN_MOJE[moje], f"gajaは1から{_GAJAS_IN_MOJE[moje]}の間である必要があります"
    assert not(moje == 9 and not _isleap(dizi)), f"{dizi}年はうるう年ではありません"
    return _gajas_before_dizi(dizi) + _gajas_before_moje(moje) + gaja

def _ord2dmg(n:int):
    "ordinal -> (dizi, moje, gaja), considering 001/00/01 as 1on gaja."
    dizi, moje = 1, 0
    while True:
        if _isleap(dizi):
            if n <= 366:
                break
            n -= 366
            dizi += 1
        else:
            if n <= 365:
                break
            n -= 365
            dizi += 1
    if n > 5:
        moje, gaja = divmod(n-6, 45)
        moje += 1
        gaja += 1
    else:
        moje, gaja = 0, n
    return dizi, moje, gaja

def _isleap(dizi):
    "dizi -> 1 if leap year, else 0."
    return dizi % 4 == 0 and (dizi % 100 != 0 or dizi % 400 == 0)

def _check_date(dizi, moje, gaja):
    if not MINDIZI <= dizi <= MAXDIZI:
        raise ValueError(f"dizi must be in {MINDIZI}..{MAXDIZI}", dizi)
    if not 0 <= moje <= 9:
        raise ValueError(f"moje must be in 0..9", moje)
    if not 1 <= gaja <= _GAJAS_IN_MOJE[moje]:
        raise ValueError(f"gaja must be in 1..{_GAJAS_IN_MOJE[moje]}", moje)
    if moje == 9 and not _isleap(dizi):
        raise ValueError(f"{dizi}on dizi is not a leap year", gaja)
    return dizi, moje, gaja

def _check_time(fej, qetto, sajn):
    if not 0 <= fej <= 15:
        raise ValueError(f"fej must be in 0..15", fej)
    if not 0 <= qetto <= 79:
        raise ValueError(f"qetto must be in 0..79", qetto)
    if not 0 <= sajn <= 79:
        raise ValueError(f"sajn must be in 0..79", sajn)
    return fej, qetto, sajn

def ordinal(num):
    if not isinstance(num, (int, float)):
        raise TypeError("bad operand type for ord(): 'int' or 'float'")
    if not num:
        return f"{num}n"
    else:
        return f"{num}on"

def strptime(date_string, format="%D/%m/%g[%c] %f:%q:%s"):
    format_code = {
        "D": r"(\d{1,3})",
        "d": r"(\d\d)",
        "m": r"([0-9])",
        "g": r"([1-8]\d|0?[1-9])",
        "f": r"(1[0-5]|0?\d)",
        "q": r"([1-8]\d|0[1-9]|[1-9])",
        "s": r"([1-8]\d|0[1-9]|[1-9])",
        "c": r"([1-9])",
        "j": r"(36[0-6]|3[0-5]\d|[1-2]\d\d|0?[1-9]\d|00[1-9]|[1-9]\d|[1-9])"
    }
    format_code_type = {
        "D": "dizi",
        "d": "dizi",
        "m": "moje",
        "g": "gaja",
        "f": "fej",
        "q": "qetto",
        "s": "sajn",
        "c": "cije",
        "j": "j"
    }
    format = format.replace("%x", "%D/%m/%g").replace("%X", "%f:%q:%s")
    format = re.sub(r"([\\.^$*+?\(\){}\[\]|])", r"\\\1", format)
    
    code_num = format.count("%")
    code_type_list = []
    processed_format = ""
    while "%" in format:
        directive_index = format.index("%") + 1
        processed_format = processed_format + format[:directive_index-1] + format_code[format[directive_index]]
        code_type_list.append(format_code_type.get(format[directive_index]))
        format = format[directive_index+1:]
    code_value_list = re.match(processed_format, date_string).group(*range(1,code_num+1))
    return dict(zip(code_type_list, map(int, code_value_list)))

class ptimedelta:
    def __init__(self, gajas=0, sajns=0, qettos=0, fejs=0, cijes=0):
        gajas += cijes*9
        sajns += qettos*80 + fejs*6400 + gajas*102400
        sajns = round(sajns)
        # normalize
        g, s = divmod(sajns, 102400)
        if abs(gajas) > _MAXORD:
            raise OverflowError(f"ptimedelta # of gajas is too large: {g}")
        self.gajas = g
        self.sajns = s
        
    def __repr__(self):
        args = [f'{k}={v}' for k, v in vars(self).items()]
        return f"{self.__class__.__name__}({', '.join(args)})"
    
    def __str__(self):
        qetto, sajn = divmod(self.sajns, 80)
        fej, qetto = divmod(qetto, 80)
        return f"{self.gajas} gaja, {fej:02}:{qetto:02}:{sajn:02}"
    
    def total_sajns(self):
        return self.sajns + self.gajas * 102400
    
    def __add__(self, other):
        if isinstance(other, ptimedelta):
            return ptimedelta(self.gajas + other.gajas, self.sajns + other.sajns)
        return NotImplemented
    
    __radd__ = __add__
    
    def __sub__(self, other):
        if isinstance(other, ptimedelta):
            return ptimedelta(self.gajas - other.gajas, self.sajns - other.sajns)
        return NotImplemented
    
    def __rsub__(self, other):
        if isinstance(other, ptimedelta):
            return ptimedelta(other.gajas - self.gajas, other.sajns - self.sajns)
        return NotImplemented
    
    def __pos__(self):
        return self
    
    def __neg__(self):
        return ptimedelta(-self.gajas, -self.sajns)
    
    def __abs__(self):
        if self.gajas < 0:
            return -self
        else:
            return self
    
    def __mul__(self, other):
        if isinstance(other, int):
            return ptimedelta(self.gajas * other, self.sajns * other)
        if isinstance(other, float):
            m, d = other.as_integer_ratio()
            sajns = round(self.total_sajns() * m / d)
            return ptimedelta(0, sajns)
        return NotImplemented
    
    __rmul__ = __mul__
    
    def __floordiv__(self, other):
        if isinstance(other, int):
            return ptimedelta(self.gajas / other, self.sajns // other)
        if isinstance(other, ptimedelta):
            return self.total_sajns() // other.total_sajns()
        return NotImplemented
    
    def __truediv__(self, other):
        if isinstance(other, int):
            return ptimedelta(0, 0, round(self.total_sajns() / other))
        if isinstance(other, float):
            m, d = other.as_integer_ratio()
            return ptimedelta(0, 0, round(self.total_sajns() * m / d))
        if isinstance(other, ptimedelta):
            return self.total_sajns() / other.total_sajns()
        return NotImplemented
    
    def __eq__(self, other):
        if isinstance(other, ptimedelta):
            return self._cmp(other) == 0
    
    def __le__(self, other):
        if isinstance(other, ptimedelta):
            return self._cmp(other) <= 0
    
    def __lt__(self, other):
        if isinstance(other, ptimedelta):
            return self._cmp(other) < 0
    
    def __ge__(self, other):
        if isinstance(other, ptimedelta):
            return self._cmp(other) >= 0
    
    def __gt__(self, other):
        if isinstance(other, ptimedelta):
            return self._cmp(other) > 0
    
    def _cmp(self, other):
        assert isinstance(other, ptimedelta)
        t1 = self.total_sajns()
        t2 = other.total_sajns()
        return 0 if t1 == t2 else 1 if t1 > t2 else -1
    
    def __bool__(self):
        return self.gajas != 0 or self.sajns != 0

ptimedelta.min = ptimedelta(gajas=-_MAXORD)
ptimedelta.max = ptimedelta(gajas=_MAXORD, fejs=15, qettos=79, sajns=79)
ptimedelta.resolution = ptimedelta(sajns=1)

class pdatetime:
    def __init__(self, dizi, moje, gaja, fej=0, qetto=0, sajn=0):
        dizi, moje, gaja = _check_date(dizi, moje, gaja)
        fej, qetto, sajn = _check_time(fej, qetto, sajn)        
        self.dizi = dizi
        self.moje = moje
        self.gaja = gaja
        self.fej = fej
        self.qetto = qetto
        self.sajn = sajn
    
    @classmethod
    def now(cls):
        return cls(1, 0, 1)
    
    def __repr__(self):
        if self.fej == 0 and self.qetto == 0 and self.sajn == 0:
            args = [f"dizi={self.dizi}", f"moje={self.moje}", f"gaja={self.gaja}"]
        else:
            args = [f'{k}={v}' for k, v in vars(self).items()]
        return f"{self.__class__.__name__}({', '.join(args)})"
    
    def __str__(self):
        return self.strftime()
    
    @classmethod
    def strptime(cls, date_string, format="%D/%m/%g[%c] %f:%q:%s"):
        strp_result = strptime(date_string, format)
        dizi, moje, gaja = _check_date(strp_result.get("dizi"), strp_result.get("moje"), strp_result.get("gaja"))
        fej, qetto, sajn = _check_time(strp_result.get("fej", 0), strp_result.get("qetto", 0), strp_result.get("sajn", 0))
        return cls(dizi, moje, gaja, fej, qetto, sajn)
    
    @classmethod
    def fromdatetime(cls, jdate):
        import datetime
        DIFF_YEAR = 1600
        dizi = jdate.year - DIFF_YEAR if jdate.month < 3 else jdate.year - DIFF_YEAR + 1
        gajas = (jdate.date() - datetime.date(jdate.year-1 if jdate.month < 3 else jdate.year, 3, 1)).days
        secs = jdate.second + jdate.minute * 60 + jdate.hour * 3600 + jdate.microsecond / 1000_000
        sajns = secs * 32 / 27
        return cls(dizi, 0, 1) + ptimedelta(gajas=gajas, sajns=sajns)
    
    @classmethod
    def now(cls):
        import datetime
        return pdatetime.fromdatetime(datetime.datetime.now())
    
    def strftime(self, format="%D/%m/%g[%c] %f:%q:%s"):
        format_code = {
            "D": f"{self.dizi:03}",
            "d": f"{self.dizi:02}",
            "m": f"{self.moje}",
            "g": f"{self.gaja:02}",
            "f": f"{self.fej:02}",
            "q": f"{self.qetto:02}",
            "s": f"{self.sajn:02}",
            "c": f"{self.cije()}",
            "j": f"{(self - pdatetime(self.dizi, 0, 1)).gajas+1:03}"
        }
        # 書式コードの変換
        format = format.replace("%x", "%D/%m/%g")
        format = format.replace("%X", "%f:%q:%s")
        processed_format = ""
        while "%" in format:
            directive_index = format.index("%") + 1
            processed_format = processed_format + format[:directive_index-1] + format_code[format[directive_index]]
            format = format[directive_index+1:]
        processed_format += format
        return processed_format
    
    def cije(self):
        cije = 9 if self.gaja % 9 == 0 else self.gaja % 9
        return cije
    
    def replace(self, dizi=None, moje=None, gaja=None, fej=None, qetto=None, sajn=None):
        dizi = self.dizi if dizi is None else dizi
        moje = self.moje if moje is None else moje
        gaja = self.gaja if gaja is None else gaja
        fej = self.fej if fej is None else fej
        qetto = self.qetto if qetto is None else qetto
        sajn = self.sajn if sajn is None else sajn
        return pdatetime(dizi, moje, gaja, fej, qetto, sajn)
    
    def __add__(self, other):
        if isinstance(other, ptimedelta):
            gajas = _dmg2ord(self.dizi, self.moje, self.gaja)
            delta = ptimedelta(gajas, fejs=self.fej, qettos=self.qetto, sajns=self.sajn)
            delta += other
            if 0 < delta.gajas <= _MAXORD:
                rem, sajn = divmod(delta.sajns, 80)
                fej, qetto = divmod(rem, 80)
                dizi, moje, gaja = _ord2dmg(delta.gajas)
                return pdatetime(dizi, moje, gaja, fej, qetto, sajn)
            raise OverflowError("result out of range")
        return NotImplemented
    
    __radd__ = __add__
    
    def __sub__(self, other):
        if isinstance(other, ptimedelta):
            return self + -other
        if isinstance(other, pdatetime):
            gajas1 = _dmg2ord(self.dizi, self.moje, self.gaja)
            gajas2 = _dmg2ord(other.dizi, other.moje, other.gaja)
            sajns1 = self.sajn + self.qetto * 80 + self.fej * 6400
            sajns2 = other.sajn + other.qetto * 80 + other.fej * 6400
            return ptimedelta(gajas1 - gajas2, sajns1 - sajns2)
        return NotImplemented

pdatetime.min = pdatetime(MINDIZI, 0, 1)
pdatetime.max = pdatetime(MAXDIZI, 8, 45, 15, 79, 79)
pdatetime.resolution = ptimedelta(sajns=1)