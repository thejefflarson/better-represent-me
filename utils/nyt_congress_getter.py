import math, sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../../')
import simplejson, urllib, pprint
NYT_BASE = "http://api.nytimes.com/svc/politics/"
from beckett.better_represent.utils.app_id import get_app_id
from beckett.nyt_utils.query import load_json


def get_congress_data_json(**kwargs):
    """
    Args, see: http://developer.nytimes.com/docs/congress_api
        congress-number: session of congress
        chamber: 'house' | 'senate'
        session: number of session
        votes: vote number
        member: member id
        query_file: votes, commitees, members
        search: state, district

    Note: this is pretty partial for now. 
    """

    kwargs.update({
        'app_id': get_app_id(),
        'version': 'v2',
        'response_format': 'json',
        'path': 'us/legislative/congress',
    })
    order = ["version", "path", "extra_path", "congress_number", "chamber", "member_id", "query_file"]
    return load_json(order, NYT_BASE, **kwargs)


if __name__ =="__main__":
    test = {
        'search':{
               'state':'NY',
 #              'district': '11',
            },
        'chamber': 'senate',
        'congress_number':'110',
        'query_file': 'members',
    }
    get_congress_data_json(**test)
