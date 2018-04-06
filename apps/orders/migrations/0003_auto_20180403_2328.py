# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_auto_20180324_1318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderinfo',
            name='trade_no',
            field=models.CharField(max_length=100, default='', null=True, blank=True, verbose_name='支付编号'),
        ),
    ]
