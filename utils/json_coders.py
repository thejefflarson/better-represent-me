import simplejson as json
from datetime import date, datetime


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        return json.JSONEncoder.default(self, obj)

def date_decoder(dct):
    if 'date' in dct:
        dt = datetime.strptime(dct['date'],"%Y-%m-%d")
        dct['date'] = date(dt.year, dt.month, dt.day)
    return dct
