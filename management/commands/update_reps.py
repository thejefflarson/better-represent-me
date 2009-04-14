import os, sys, time
from django.core.management.base import BaseCommand
from better_represent.utils.get_reps import RepGetter
LOCKFILE = "/tmp/update_reps.lock"


class Command(BaseCommand):
    def handle(self, **options):
        try:
            lockfile = os.open(LOCKFILE, os.O_CREAT | os.O_EXCL)
        except OSError:
            sys.exit(0)
        try:
            self.update_reps(int(options.get('verbosity', 0)))
        finally:
            os.close(lockfile)
            os.unlink(LOCKFILE)

    def update_reps(self, verbosity):
        if verbosity==False:
            sys.stdout = open("out.txt","w")
            sys.stderr = open("err.txt","w")
        rng = range(112)[102:]
        rng.reverse()
        rg = RepGetter()
        if verbosity:
            from better_represent.utils.progressbar import ProgressBar
            prog = ProgressBar(minValue=0,maxValue=len(rng)) 
        for i in rng:
            if verbosity:
                prog(prog.amount+1, 'Importing: ')
            rg.get_representatives(i, 'House')
            time.sleep(5)
            rg.get_representatives(i, 'Senate')
            time.sleep(5)
