# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import protocol.models
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('protocol', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('attachment', models.FileField(upload_to=protocol.models.get_storage_location)),
                ('body', models.TextField(blank=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='attachment',
            name='message',
        ),
        migrations.RemoveField(
            model_name='message',
            name='communication',
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ('human_path',), 'verbose_name_plural': 'Categories'},
        ),
        migrations.AlterModelOptions(
            name='communication',
            options={'ordering': ('submitted',), 'get_latest_by': 'submitted'},
        ),
        migrations.AddField(
            model_name='category',
            name='human_path',
            field=models.CharField(default=datetime.datetime(2017, 6, 1, 12, 57, 40, 109527, tzinfo=utc), max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='category',
            name='index',
            field=models.PositiveIntegerField(default=datetime.datetime(2017, 6, 1, 12, 57, 50, 118033, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='category',
            name='description',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.DeleteModel(
            name='Attachment',
        ),
        migrations.DeleteModel(
            name='Message',
        ),
        migrations.AddField(
            model_name='document',
            name='communication',
            field=models.ForeignKey(to='protocol.Communication'),
        ),
    ]
