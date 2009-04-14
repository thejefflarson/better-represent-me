
from south.db import db
from django.db import models
from better_represent.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'RepStat.rep'
        db.add_column('better_represent_repstat', 'rep', models.ForeignKey(orm.GenericRep))
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'RepStat.rep'
        db.delete_column('better_represent_repstat', 'rep_id')
        
    
    
    models = {
        'better_represent.genericrep': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        }
    }
    
    
