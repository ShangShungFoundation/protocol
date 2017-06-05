# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import protocol.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('attachment', models.FileField(upload_to=protocol.models.get_storage_location)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255)),
                ('path', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=255, null=True, blank=True)),
                ('parent', models.ForeignKey(blank=True, to='protocol.Category', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Communication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('protocol', models.CharField(unique=True, max_length=255, db_index=True)),
                ('frm', models.CharField(max_length=255, verbose_name='from')),
                ('to', models.CharField(max_length=255)),
                ('subject', models.TextField()),
                ('submitted', models.DateTimeField(auto_now_add=True)),
                ('is_incoming', models.BooleanField()),
                ('location', models.CharField(help_text='indicate storage location for ordinary (physical) communications', max_length=255, null=True, blank=True)),
                ('category', models.ForeignKey(to='protocol.Category')),
            ],
            options={
                'get_latest_by': 'submitted',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('body', models.TextField()),
                ('communication', models.ForeignKey(to='protocol.Communication')),
            ],
        ),
        migrations.AddField(
            model_name='attachment',
            name='message',
            field=models.ForeignKey(to='protocol.Message'),
        ),
    ]
