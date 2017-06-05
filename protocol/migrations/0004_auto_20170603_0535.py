# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('protocol', '0003_auto_20170601_1319'),
    ]

    operations = [
        migrations.CreateModel(
            name='StorageLocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
            ],
        ),
        migrations.RemoveField(
            model_name='communication',
            name='location',
        ),
        migrations.AddField(
            model_name='document',
            name='metadata',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='communication',
            name='storage',
            field=models.ForeignKey(blank=True, to='protocol.StorageLocation', null=True),
        ),
    ]
