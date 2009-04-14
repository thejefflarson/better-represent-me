import os, sys
from django.core.management.base import BaseCommand
from better_represent.search import NewsAggregator
from better_represent.models import *
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
        a = NewsAggregator()
        a.get_multiple([(" ".join([n.first_name, n.last_name]), [n.get_type_display()], n) for n in representatives], VERBOSE=verbosity)
        if verbosity:
            from better_represent.utils.progressbar import ProgressBar
            prog = ProgressBar(minValue=0,maxValue=len(a.items)) 
        for item in a.items:
            if verbosity:
                prog(prog.amount+1, 'Importing: ')
            try:
                obj = item['extra'].repstat_set.get(stat=item['datetime'])
            except RepStat.DoesNotExist:
                try:
                    obj = RepStat(stat=item['datetime'], rep=item['extra'])
                    obj.set_hash(item['title'])
                    obj.save()
                except Exception, e:
                    if verbosity:
                        print "error %s" % e.message
