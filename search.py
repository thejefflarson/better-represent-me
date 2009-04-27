import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
import simplejson, urllib2, urllib, sys, re
from datetime import datetime
from itertools import *
from operator import itemgetter
from pprint import pprint
from django.utils.http import urlquote_plus
from django.utils.encoding import iri_to_uri
from better_represent.utils.app_id import *

class Query:
    def __init__(self):
        self.items = []

    class Map:
        """ maps fields from source query to these standard fields:
            url
            title
            org
            homepage
            datetime
        """
        pass
    
    def _parse_mapping(self, raw_items, extra):
        map = self.Map()
        for key in self.result_keys:
            try:
                raw_items = raw_items[key]
            except (KeyError, TypeError):
                return
        for raw_item in raw_items:
            attrs = dir(map)
            mapped_item = {}
            callables = []
            for attr in attrs:
                if re.search("__.*__", attr) == None:
                    if callable(getattr(map, attr)):
                        callables.append(attr)
                    else:
                        mapped_item[attr] = raw_item[getattr(map, attr)]
            for call in callables:
                getattr(map, call)(raw_item, mapped_item)
            mapped_item['extra'] = extra
            mapped_item['verb'] = self.verb
            self.items.append(mapped_item)

    def _query(self, url, extra):
        try:
            user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
            headers = {'Referer': 'http://stag.ceocampaigncontributions.info/', #change when ready
                        'user_agent': user_agent
                        }
            request = urllib2.Request(url, None, headers) 
            response = urllib2.urlopen(request) 
            self._parse_mapping(simplejson.load(response), extra)
        except ValueError, e:
            sys.stderr.write('error: %s url: %s resp: %s\n' %(e,url, response.read()))
            return 'error: %s url: %s\n' %(e,url)

    def get_items(self, query, oars):
        pass


class YahooNews(Query):
    YAHOO_BOSS_KEY = get_boss_key()
    YAHOO_URL = 'http://boss.yahooapis.com/ysearch/news/v1/'
    def __init__(self):
        Query.__init__(self)
        self.result_keys = ['ysearchresponse', 'resultset_news']
        self.args = { 'appid': self.YAHOO_BOSS_KEY,
                    'age': '7d' }
        self.verb = 'appeared in'
    
    class Map:
        url = 'url'
        title = 'title'
        org = 'source'
        homepage = 'sourceurl'
        def date(self, item, mapped_item):
            fields = ['date', 'time']
            target_field = 'datetime'
            format_string = "%Y/%m/%d %H:%M:%S"
            mapped_item[target_field] = datetime.strptime(" ".join([item[n] for n in fields]), format_string)
        
        def source(self, item, mapped_item):
            mapped_item['source'] = 'yahoo'

    def get_items(self, query, oars, extra):
        query = "%s \"%s\"" %(" ".join(oars), query)
        url = self.YAHOO_URL + iri_to_uri(urlquote_plus(query)) + "?" + urllib.urlencode(self.args)
        self._query(url, extra)
        return self.items

class GoogleNews(Query):
    GOOGLE_KEY = get_google_key()
    GOOGLE_URL = 'http://ajax.googleapis.com/ajax/services/search/news'
    def __init__(self):
        Query.__init__(self)
        self.result_keys = ['responseData', 'results']
        self.args = { 'v':'1.0',
                      'scoring':'d',
                      'key': self.GOOGLE_KEY
            }
        self.verb = 'appeared in'

    class Map:
        url = 'unescapedUrl'
        title = 'titleNoFormatting'
        org = 'publisher'
        def homepage(self, item, mapped_item):
            field = 'unescapedUrl'
            target_field = 'homepage'
            mapped_item[target_field] = re.search("^(?P<url>http://.*?/).*", item[field]).group('url')

        def date(self, item, mapped_item):
            field = 'publishedDate'
            target_field = 'datetime'
            format_string = "%a, %d %b %Y %H:%M:%S"
            mapped_item[target_field] = datetime.strptime(" ".join(item[field].split(" ")[:-1]), format_string) # forget about  timezone it's wonky
        
        def source(self, item, mapped_item):
            mapped_item['source'] = 'google'


    def get_items(self, query, oars, extra):
        query = '%s %s' %( " ".join(oars), query)
        self.args['q'] = iri_to_uri(urlquote_plus(query))
        url = self.GOOGLE_URL + "?" + urllib.urlencode(self.args)
        self._query(url, extra)
        return self.items

class NYTimesVotes(Query):
    ## in my dreams
    #from better_represent.utils import get_congress_data_json
    def __init__(self):
        Query.__init__(self)
        self.result_keys = ['votes']
        self.args = {
                        '':'',
                        '':'',
                        '':'',
                    }
    
    class Map:
        def url(self, item, mapped_item):
            pass
        def org(self, item, mapped_item):
            pass
        def homepage(self, item, mapped_item):
            pass
        def title(self, item, mapped_item):
            pass
        def date(self, item, mapped_item):
            pass

    def get_items(self, extra, queries):
        for query in queries:
            get_congress_data_json(query)
        
        

class NewsAggregator:
    def __init__(self):
        self.g = GoogleNews()
        self.y = YahooNews()
        self.items = []

    def _uniquify(self, iterable, key=None):
        #from http://docs.python.org/library/itertools.html
        seen = set()
        seen_add = seen.add
        if key is None:
            for element in iterable:
                if element not in seen:
                    seen_add(element)
                    yield element
        else:
            for element in iterable:
                k = key(element)
                if k not in seen:
                    seen_add(k)
                    yield element

    def get_items(self, query, oars, extra):
        self.items.extend(self.g.get_items(query, oars, extra))
        self.items.extend(self.y.get_items(query, oars, extra))
        return self.items

    def get_nyt_items(self, queries):
        # self.items.extend(self.n.get_items(extra, queries))
        pass

    def get_multiple(self, queries, VERBOSE=0):
        """ takes a list of tuples (query, oars, extra) and returns a dict, the oars are refinements, extra is an annotation must be a django object """
        if VERBOSE:
            from better_represent.progressbar import ProgressBar
            prog = ProgressBar(minValue=0,maxValue=len(queries)) 
        for query in queries:
            if VERBOSE:
                prog(prog.amount+1, 'Searching: ')
            self.get_items(*query)
        self.items.sort(cmp=lambda x, y: cmp(x['datetime'], y['datetime']), reverse=True)
        self.items = [n for n in self._uniquify(self.items, key=lambda x: x['title'])]


if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../")
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../")
    from django.core.management import setup_environ
    from beckett import settings 
    setup_environ(settings)
    from better_represent.models import *
    import hashlib
    
    
    a = NewsAggregator()
    reps = [GenericRep.objects.get(first_name="John", last_name="Kerry")]#, GenericRep.objects.get(first_name="Yvette", last_name="Clarke")]
    a.get_multiple([(" ".join([n.first_name, n.last_name]), [n.get_type_display()], n) for n in reps])
    pprint(a.items)
    for item in a.items:
        print hashlib.md5(item['title'].encode("utf-8")).hexdigest()
