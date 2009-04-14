import subprocess
import simplejson as json
from math import fabs
from hashlib import md5
from datetime import date, timedelta, datetime
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.template.defaultfilters import slugify
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models.query import QuerySet
from django.db.models import Count, Max
from beckett.polygons.models import Zip, CongressionalDistrict, State
from django.core.cache import cache
# Create your models here.


def address_normalize(address):
    return slugify(address.lower()).replace("-", " ")

class Address(models.Model):
    """
    simple address model, tries to geocode, and if unsuccessful doesn't save and raises AddressPointNotFoundError
    """
    address = models.TextField(unique=True)
    slug = models.SlugField(unique=True)
    zip = models.ForeignKey(Zip, related_name="%(class)s_related")
    point = models.PointField(srid=4326)
    objects = models.GeoManager()
    class Meta:
        unique_together = ('address', 'zip')

    class AddressPointNotFoundError(Exception):
        def __init__(self, address, json):
            self.address = address
            self.json = json
        def __str__(self):
            return "address: %s GeoCoder Returned %s" % (self.address, str(self.json))
    

    def save(self, force_insert=False, force_update=False):
        self.address = address_normalize(self.address)
        self.slug = slugify(self.address)
        try:
            geocoded = json.loads(subprocess.Popen(["/web/geocode_db/query.pl", 
                        "/web/geocode_db/geocoder.db", 
                        self.address], 
                        stdout=subprocess.PIPE).communicate()[0]).pop()
            self.zip, created = Zip.objects.get_or_create(code=geocoded["zip"])
            self.point = Point(float(geocoded["long"]), float(geocoded["lat"]))
        except (KeyError, IndexError):
            raise self.AddressPointNotFoundError(address=self.address, 
                                                    json=subprocess.Popen(["/web/geocode_db/query.pl", 
                                                                            "/web/geocode_db/geocoder.db", 
                                                                            self.address], 
                                                                            stdout=subprocess.PIPE).communicate())
        super(Address, self).save(force_insert, force_update)

    @models.permalink
    def get_absolute_url(self):
        return ('address_detail', (), {'address_slug':self.slug})

    def __unicode__(self):
        return u'%s' % (self.address)

class Congress(models.Model):
    chamber = models.TextField()
    session = models.IntegerField()
    class Meta:
        unique_together = ('chamber', 'session')
        verbose_name_plural = 'congresses'


class Party(models.Model):
    name = models.CharField(max_length=24, unique=True)


        
class RepManager(models.Manager):
    use_for_related_fields = True
    def get_query_set(self):
        return self.model.QuerySet(self.model)


class GenericRep(models.Model):
    TYPE = (
            ('H', 'Representative'),
            ('S', 'Senator'),
            )
    type = models.CharField(max_length=1, choices=TYPE)
    member_id = models.CharField(max_length=10, unique=True)
    first_name = models.TextField()
    last_name = models.TextField()
    party = models.ForeignKey(Party)
    state = models.ForeignKey(State)
    end_date = models.DateField(null=True)
    congresses = models.ManyToManyField(Congress, through='CongressMembership')
    district = models.ForeignKey(CongressionalDistrict, null=True)
    objects = RepManager()
    
    @property
    def max_stats(self):
        value = self.stats.all().extra(select={'date': "date_trunc('day', \"better_represent_repstat\".\"stat\")"},).values('date').annotate(num_stats=Count('id')).order_by('-num_stats')[0]['num_stats']
        return value
    
    def stats_by_day(self, timeframe=timedelta(days=30), start=date.today()):
        raw_days = [n for n in 
                    self.stats.filter(stat__gt=start-timeframe).extra(
                        select={'date': "date_trunc('day', \"better_represent_repstat\".\"stat\")"}, 
                    ).values('date').annotate(num_stats=Count('id')).order_by('-date')]
        data = [{'date':start-timedelta(days=n), 'num_stats':0} for n in range(timeframe.days)]
        for day in raw_days:
            just_the_date = date(day['date'].year, day['date'].month, day['date'].day)
            delta = start-just_the_date
            if 0 < delta.days < timeframe.days:
                day['date'] = just_the_date
                data[delta.days-1] = day
        return data
    
    class QuerySet(QuerySet):
        def live(self):
            return self.filter(**{'end_date__gt':date.today()})
        def old(self):
            return self.filter(**{'end_date__lt':date.today()})
        def latest_stats_count(self, timeframe=timedelta(days=30), start=date.today()):
            return self.annotate(Count('stats')).extra(where=["stat > '%s'" % (start-timeframe)]).order_by('-stats__count')
        def annotate_max_stats(self):
            content_type = ContentType.objects.get(app_label="better_represent", model=self.model.__name__.lower())
            return self.extra(select={'stats__max': 'SELECT "max_count" FROM "better_represent_repstat_max_stat" WHERE "better_represent_%s"."id"="better_represent_repstat_max_stat"."object_id" AND "better_represent_repstat_max_stat"."content_type_id"=%s' % (self.model.__name__.lower(),content_type.id)},)

    class Meta:
        pass

    def __unicode__(self):
        return "%s %s %s" % ( self.get_type_display(), self.first_name, self.last_name)

    def save(self, force_insert=False, force_update=False):
        if self.district and self.type=='S':
            raise IntegrityError
        return super(GenericRep, self).save(force_insert, force_update)


class CongressMembership(models.Model):
    title = models.CharField(max_length=64)
    congress = models.ForeignKey(Congress)
    rep = models.ForeignKey(GenericRep)
    class Meta:
        pass



class RepStat(models.Model):
    stat = models.DateField()
    hash = models.CharField(max_length=128)
    rep = models.ForeignKey(GenericRep)

    def set_hash(self, title):
        hash = md5(title.encode('utf-8')).hexdigest()
        self.hash = hash

    def __unicode__(self):
        return self.stat

    class Meta:
        unique_together=( 'stat', 'hash')
