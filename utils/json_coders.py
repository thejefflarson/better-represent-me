import simplejson as json
from datetime import date, datetime, timedelta
import calendar


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return calendar.timegm(obj.timetuple())*1000
        return json.JSONEncoder.default(self, obj)

def date_decoder(dct):
    if 'date' in dct:
        dct['date'] = date.fromtimestamp(int(dct['date'])/1000)+timedelta(days=1) # huh?
    return dct
