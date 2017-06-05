# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import protocol.models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('protocol', '0002_auto_20170601_1257'),
    ]

    operations = [
        migrations.AddField(
            model_name='communication',
            name='is_digital',
            field=models.BooleanField(default=datetime.datetime(2017, 6, 1, 13, 19, 51, 944834, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='document',
            name='attachment',
            field=models.FileField(null=True, upload_to=protocol.models.get_storage_location, blank=True),
        ),
    ]
