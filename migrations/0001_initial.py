
from south.db import db
from django.db import models
from better_represent.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'CongressMembership'
        db.create_table('better_represent_congressmembership', (
            ('rep', models.ForeignKey(orm.GenericRep)),
            ('id', models.AutoField(primary_key=True)),
            ('congress', models.ForeignKey(orm.Congress)),
            ('title', models.CharField(max_length=64)),
        ))
        db.send_create_signal('better_represent', ['CongressMembership'])
        
        # Adding model 'GenericRep'
        db.create_table('better_represent_genericrep', (
            ('first_name', models.TextField()),
            ('last_name', models.TextField()),
            ('district', models.ForeignKey(orm['polygons.CongressionalDistrict'], null=True)),
            ('end_date', models.DateField(null=True)),
            ('state', models.ForeignKey(orm['polygons.State'])),
            ('member_id', models.CharField(unique=True, max_length=10)),
            ('party', models.ForeignKey(orm.Party)),
            ('type', models.CharField(max_length=1)),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('better_represent', ['GenericRep'])
        
        # Adding model 'Congress'
        db.create_table('better_represent_congress', (
            ('chamber', models.TextField()),
            ('session', models.IntegerField()),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('better_represent', ['Congress'])
        
        # Adding model 'Address'
        db.create_table('better_represent_address', (
            ('slug', models.SlugField(unique=True)),
            ('point', models.PointField(srid=4326)),
            ('id', models.AutoField(primary_key=True)),
            ('zip', models.ForeignKey(orm['polygons.Zip'], related_name="%(class)s_related")),
            ('address', models.TextField(unique=True)),
        ))
        db.send_create_signal('better_represent', ['Address'])
        
        # Adding model 'Party'
        db.create_table('better_represent_party', (
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField(unique=True, max_length=24)),
        ))
        db.send_create_signal('better_represent', ['Party'])
        
        # Adding model 'RepStat'
        db.create_table('better_represent_repstat', (
            ('stat', models.DateField()),
            ('hash', models.CharField(max_length=128)),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('better_represent', ['RepStat'])
        
        # Adding ManyToManyField 'GenericRep.stats'
        db.create_table('better_represent_genericrep_stats', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('genericrep', models.ForeignKey(GenericRep, null=False)),
            ('repstat', models.ForeignKey(RepStat, null=False))
        ))
        
        # Adding ManyToManyField 'GenericRep.congresses'
        db.create_table('better_represent_congressmembership', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('rep', models.ForeignKey(GenericRep, null=False)),
            ('congress', models.ForeignKey(Congress, null=False))
        ))
        
        # Creating unique_together for [address, zip] on Address.
        db.create_unique('better_represent_address', ['address', 'zip_id'])
        
        # Creating unique_together for [chamber, session] on Congress.
        db.create_unique('better_represent_congress', ['chamber', 'session'])
        
        # Creating unique_together for [stat, hash] on RepStat.
        db.create_unique('better_represent_repstat', ['stat', 'hash'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'CongressMembership'
        db.delete_table('better_represent_congressmembership')
        
        # Deleting model 'GenericRep'
        db.delete_table('better_represent_genericrep')
        
        # Deleting model 'Congress'
        db.delete_table('better_represent_congress')
        
        # Deleting model 'Address'
        db.delete_table('better_represent_address')
        
        # Deleting model 'Party'
        db.delete_table('better_represent_party')
        
        # Deleting model 'RepStat'
        db.delete_table('better_represent_repstat')
        
        # Dropping ManyToManyField 'GenericRep.stats'
        db.delete_table('better_represent_genericrep_stats')
        
        # Dropping ManyToManyField 'GenericRep.congresses'
        db.delete_table('better_represent_congressmembership')
        
        # Deleting unique_together for [address, zip] on Address.
        db.delete_unique('better_represent_address', ['address', 'zip_id'])
        
        # Deleting unique_together for [chamber, session] on Congress.
        db.delete_unique('better_represent_congress', ['chamber', 'session'])
        
        # Deleting unique_together for [stat, hash] on RepStat.
        db.delete_unique('better_represent_repstat', ['stat', 'hash'])
        
    
    
    models = {
        'polygons.congressionaldistrict': {
            'Meta': {'unique_together': "('state','district')"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'polygons.state': {
            '_stub': True,
            'fips': ('models.IntegerField', [], {'primary_key': 'True'})
        },
        'better_represent.genericrep': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'polygons.zip': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'better_represent.congress': {
            'Meta': {'unique_together': "('chamber','session')"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'better_represent.party': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'better_represent.repstat': {
            'Meta': {'unique_together': "('stat','hash')"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        }
    }
    
    
