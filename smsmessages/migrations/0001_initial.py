# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Message'
        db.create_table(u'smsmessages_message', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content', self.gf('django.db.models.fields.CharField')(max_length=160, db_index=True)),
            ('composer', self.gf('django.db.models.fields.related.ForeignKey')(related_name='composed_message', to=orm['auth.User'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'smsmessages', ['Message'])

        # Adding model 'MessageOption'
        db.create_table(u'smsmessages_messageoption', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent_msg', self.gf('django.db.models.fields.related.ForeignKey')(related_name='options', to=orm['smsmessages.Message'])),
            ('child_msg', self.gf('django.db.models.fields.related.ForeignKey')(related_name='child_msg_options', to=orm['smsmessages.Message'])),
            ('trigger_keyword', self.gf('django.db.models.fields.CharField')(max_length=160)),
            ('option_content', self.gf('django.db.models.fields.CharField')(max_length=160)),
        ))
        db.send_create_signal(u'smsmessages', ['MessageOption'])

        # Adding model 'MessageRecord'
        db.create_table(u'smsmessages_messagerecord', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content', self.gf('django.db.models.fields.CharField')(max_length=160)),
            ('message', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smsmessages.Message'], null=True, blank=True)),
            ('sender_num', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('receiver_num', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('twilio_msg_sid', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='success', max_length=10)),
            ('failed_times', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('sent_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'smsmessages', ['MessageRecord'])


    def backwards(self, orm):
        # Deleting model 'Message'
        db.delete_table(u'smsmessages_message')

        # Deleting model 'MessageOption'
        db.delete_table(u'smsmessages_messageoption')

        # Deleting model 'MessageRecord'
        db.delete_table(u'smsmessages_messagerecord')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'smsmessages.message': {
            'Meta': {'object_name': 'Message'},
            'composer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'composed_message'", 'to': u"orm['auth.User']"}),
            'content': ('django.db.models.fields.CharField', [], {'max_length': '160', 'db_index': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'smsmessages.messageoption': {
            'Meta': {'object_name': 'MessageOption'},
            'child_msg': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'child_msg_options'", 'to': u"orm['smsmessages.Message']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'option_content': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'parent_msg': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'options'", 'to': u"orm['smsmessages.Message']"}),
            'trigger_keyword': ('django.db.models.fields.CharField', [], {'max_length': '160'})
        },
        u'smsmessages.messagerecord': {
            'Meta': {'object_name': 'MessageRecord'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'failed_times': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['smsmessages.Message']", 'null': 'True', 'blank': 'True'}),
            'receiver_num': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'sender_num': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'sent_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'success'", 'max_length': '10'}),
            'twilio_msg_sid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['smsmessages']