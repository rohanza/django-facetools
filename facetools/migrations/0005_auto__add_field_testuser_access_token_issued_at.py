# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'TestUser.access_token_issued_at'
        db.add_column('facetools_testuser', 'access_token_issued_at', self.gf('django.db.models.fields.DateTimeField')(null=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'TestUser.access_token_issued_at'
        db.delete_column('facetools_testuser', 'access_token_issued_at')


    models = {
        'facetools.testuser': {
            'Meta': {'object_name': 'TestUser'},
            'access_token': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'access_token_expires': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'access_token_issued_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'login_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'})
        }
    }

    complete_apps = ['facetools']
