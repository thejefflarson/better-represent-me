import sys, os, time
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../')
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../../')

from django.core.management import setup_environ
from beckett import settings 
setup_environ(settings)
from better_represent.models import *
from polygons.models import *
from better_represent.utils.nyt_congress_getter import *

from django.db.models import Sum

class RepGetter:
    def get_representatives(self, congress, chamber):
        congress, created = Congress.objects.get_or_create(chamber=chamber, session=congress)
        resp = get_congress_data_json(**{
                    'chamber':chamber.lower(),
                    'congress_number':str(congress.session),
                    'query_file':'members',
        })
        self._save(congress, resp, chamber)

    def _save(self, congress, resp, type):
        if 'error' not in resp:
            for member in resp[0]['members']:
                try:
                    state = State.objects.get(state=member['state'])
                    party, created = Party.objects.get_or_create(name=member['party'])
                    representative, created = GenericRep.objects.get_or_create(
                                        type=type[0],
                                        member_id=member['id'],
                                        first_name=member['first_name'], 
                                        last_name=member['last_name'], 
                                        party=party, 
                                        state=state,
                                     )
                    if representative.get_type_display() == 'Representative':
                        cd = CongressionalDistrict.objects.get(state=state, district=member['district'])
                        representative.district = cd
                        representative.save()
                    time.sleep(10)
                    membership = get_congress_data_json(**{
                                        'extra_path': 'members',
                                        'query_file': representative.member_id
                    })
                    
                    if 'error' not in membership:
                        representative.end_date = membership[0]['roles'][0]['end_date']
                        representative.save()
                        for role in membership[0]['roles']:
                            m, c = CongressMembership.objects.get_or_create(congress=congress, rep=representative, title=role['title'])
                except Exception,e:
                    sys.stderr.write('error %s' % (e))



if __name__=="__main__":
    states = State.objects.all()
    sys.stdout = open("out.txt","w")
    sys.stderr = open("err.txt","w")
    rng = range(112)[102:]
    rng.reverse()
    rg = RepGetter()
    for i in rng:
        rg.get_representatives(i, 'House')
        time.sleep(5)
        rg.get_representatives(i, 'Senate')
        time.sleep(5)
