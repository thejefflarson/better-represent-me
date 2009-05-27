
from south.db import db
from django.db import models
from better_represent.models import *

class Migration:
    
    def forwards(self, orm):
        db.create_index('better_represent_repstat', ['stat','hash','rep_id'], unique=True)
    
    
    def backwards(self, orm):
        db.delete_index('better_represent_repstat', ['stat','hash','rep_id'])
        db.create_index('better_represent_repstat', ['stat','hash'], unique=True)
    
    
    models = {
        'polygons.congressionaldistrict': {
            'Meta': {'unique_together': "('state','district')"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'better_represent.congressmembership': {
            'congress': ('models.ForeignKey', ['Congress'], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'rep': ('models.ForeignKey', ['GenericRep'], {}),
            'title': ('models.CharField', [], {'max_length': '64'})
        },
        'better_represent.genericrep': {
            'congresses': ('models.ManyToManyField', ['Congress'], {'through': "'CongressMembership'"}),
            'district': ('models.ForeignKey', ['CongressionalDistrict'], {'null': 'True'}),
            'end_date': ('models.DateField', [], {'null': 'True'}),
            'first_name': ('models.TextField', [], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('models.TextField', [], {}),
            'member_id': ('models.CharField', [], {'unique': 'True', 'max_length': '10'}),
            'party': ('models.ForeignKey', ['Party'], {}),
            'state': ('models.ForeignKey', ['State'], {}),
            'type': ('models.CharField', [], {'max_length': '1'})
        },
        'polygons.zip': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'polygons.state': {
            '_stub': True,
            'fips': ('models.IntegerField', [], {'primary_key': 'True'})
        },
        'better_represent.congress': {
            'Meta': {'unique_together': "('chamber','session')"},
            'chamber': ('models.TextField', [], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'session': ('models.IntegerField', [], {})
        },
        'better_represent.address': {
            'Meta': {'unique_together': "('address','zip')"},
            'address': ('models.TextField', [], {'unique': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'point': ('models.PointField', [], {'srid': '4326'}),
            'slug': ('models.SlugField', [], {'unique': 'True'}),
            'zip': ('models.ForeignKey', ['Zip'], {'related_name': '"%(class)s_related"'})
        },
        'better_represent.party': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'unique': 'True', 'max_length': '24'})
        },
        'better_represent.repstat': {
            'Meta': {'unique_together': "('stat','hash','rep')"},
            'hash': ('models.CharField', [], {'max_length': '128'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'rep': ('models.ForeignKey', ['GenericRep'], {}),
            'stat': ('models.DateField', [], {})
        }
    }
    
    complete_apps = ['better_represent']
