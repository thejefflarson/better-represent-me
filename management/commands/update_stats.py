import os, sys
from django.core.management.base import BaseCommand
from django.db import connection
from better_represent.search import NewsAggregator
from better_represent.models import *
from persistent_store.django_tokyo_persistent_store import tyrant_store
LOCKFILE = "/tmp/update_stats.lock"


class Command(BaseCommand):
    def handle(self, **options):
        try:
            lockfile = os.open(LOCKFILE, os.O_CREAT | os.O_EXCL)
        except OSError:
            sys.exit(0)
        try:
            self.update_stats(int(options.get('verbosity', 0)))
        finally:
            os.close(lockfile)
            os.unlink(LOCKFILE)

    def update_stats(self, verbosity):
        representatives = GenericRep.objects.all().live()
        for rep in representatives: 
            a = NewsAggregator()
            a.get_multiple([(" ".join([rep.first_name, rep.last_name]), [rep.get_type_display()], rep)])
            if verbosity:
                from better_represent.utils.progressbar import ProgressBar
                prog = ProgressBar(minValue=0,maxValue=len(a.items)) 
            rep.items = a.items
            for item in a.items:
                if verbosity:
                    prog(prog.amount+1, "Importing %s: " % rep)
                try:
                    obj = item['extra'].repstat_set.get(stat=item['datetime'], hash=RepStat()._encode_hash(item['title']))
                except RepStat.DoesNotExist:
                    try:
                        obj = RepStat(stat=item['datetime'], rep=item['extra'])
                        obj.set_hash(item['title'])
                        obj.save()
                    except Exception, e:
                        if verbosity:
                            print "error %s" % e.message
