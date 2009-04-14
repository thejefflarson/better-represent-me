import os
from django.test import TestCase
from django.contrib.gis.geos import *
from django.template.defaultfilters import slugify
from beckett.better_represent.models import *
from beckett.better_represent.templatetags.graph_extras import draw_graph
from beckett.better_represent.utils.json_coders import date_decoder
from django.test.client import Client
from datetime import datetime, timedelta, date

class AddressTest(TestCase):
    def setUp(self):
        self.address_obj = Address(address="537 Clinton Ave, Brooklyn, NY 11238")
        self.bad_address_obj = Address(address="11238")
        data_dir = os.path.join(os.path.dirname(__file__), '../finance/wkt')
        def get_file(wkt_file):
            return os.path.join(data_dir, wkt_file)
        zip_obj = Zip.objects.create(code="11238", poly=fromfile(get_file("nz.wkt")))
        self.point_obj = Point(-73.966664,40.682241)
        self.client = Client()
        self.address_obj.save()

    def test_save(self):
        self.failUnlessEqual(self.address_obj.address, "537 clinton ave brooklyn ny 11238")
        self.failUnlessEqual(self.address_obj.slug, slugify(self.address_obj.address))
        self.failUnlessEqual(self.address_obj.point.x, self.point_obj.x)
        self.failUnlessEqual(self.address_obj.point.y, self.point_obj.y)
        self.failUnlessEqual(self.address_obj.zip, Zip.objects.filter(code='11238')[0])

    def test_bad_save(self):
        self.assertRaises(self.bad_address_obj.AddressPointNotFoundError, self.bad_address_obj.save)

    def validate_response(self, response, code):
        self.failUnlessEqual(response.status_code, code)

    def test_view_good_address_get(self):
        response = self.client.post('/better_represent/', {'address': '537 Clinton Ave, Brooklyn, NY 11238'})
        self.validate_response(response, 302)
    
    def test_view_slightly_diff_address_get(self):
        response = self.client.post('/better_represent/', {'address': '537 clinton Ave BrOOklyn, NY 11238'})
        self.validate_response(response, 302)
    
    def test_view_good_address_insert(self):
        response = self.client.post('/better_represent/', {'address': '1600 Pennsylvania Avenue NW, Washington DC 20502'})
        self.validate_response(response, 302)
    
    def test_view_short_address_get(self):
        response = self.client.post('/better_represent/', {'address': '537 Clinton Ave'})
        self.validate_response(response, 302)

    def test_view_bad_address(self):
        response = self.client.post('/better_represent/', {'address': '123kfjkldjflkj'})
        self.validate_response(response, 200)

class GenRepTest(TestCase):
    def setUp(self):
        data_dir = os.path.join(os.path.dirname(__file__), '../finance/wkt')
        def get_file(wkt_file):
            return os.path.join(data_dir, wkt_file)
        self.state = State.objects.create(state='NY', fips=1, poly=fromfile(get_file("nz.wkt")))
        self.cd = CongressionalDistrict.objects.create(state=self.state, district=1, poly=fromfile(get_file("nz.wkt")))
        self.party = Party.objects.create(name="Democrat")
        self.rep = Representative.objects.create(member_id="000001", first_name="Barney", last_name="Frank", party=self.party,  district=self.cd, state=self.state)
        self.stat1 = RepStat.objects.create(stat=datetime.now(), content_object=self.rep)
        self.stat2 = RepStat.objects.create(stat=datetime.now()-timedelta(days=7), content_object=self.rep)
        self.stat3 = RepStat.objects.create(stat=datetime.now()-timedelta(days=35), content_object=self.rep)
        self.stat4 = RepStat.objects.create(stat=datetime.now()-timedelta(days=35)+timedelta(minutes=5), content_object=self.rep)

class RepresentativeTest(GenRepTest):
    def test_rep_current_count(self):
        self.failUnlessEqual(Representative.objects.all().latest_stats_count(timeframe=timedelta(days=30))[0].stats__count, 2)
        self.failUnlessEqual(sum(n['num_stats'] for n in self.rep.stats_by_day(timeframe=timedelta(days=30))), Representative.objects.all().latest_stats_count(timeframe=timedelta(days=30))[0].stats__count)

    def test_rep_stats_by_date_range(self):
        self.failUnlessEqual(len(self.rep.stats_by_day(timeframe=timedelta(days=30))), 30)
        self.failUnlessEqual(self.rep.stats_by_day(timeframe=timedelta(days=30), start=date.today()-timedelta(days=32))[3]['num_stats'], 0)
        self.failUnlessEqual(len(self.rep.stats_by_day(timeframe=timedelta(days=60))), 60)

    def test_max_rep_stats(self):
        self.failUnlessEqual(self.rep.max_stats, 2)

    def test_max_all_rep_stats(self):
        self.failUnlessEqual(Representative.objects.all().annotate_max_stats()[0].stats__max, 2)

class GraphTest(GenRepTest):
    def test_graph(self):
        self.graph_data = draw_graph([self.rep])['json']
        from_json = json.loads(self.graph_data, encoding='utf-8', object_hook=date_decoder)[str(self.rep)]
        from_db = self.rep.stats_by_day()
        from_json.reverse()
        i = 0
        for item in from_json:
            self.failUnlessEqual(item.values(), from_db[i].values())
            i += 1
