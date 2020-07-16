# Generated by Django 2.2.12 on 2020-04-02 20:22

import apps.shipments.models.shipment
from django.db import migrations, models
import enumfields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('shipments', '0015_aftership_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalshipment',
            name='gtx_validation',
            field=enumfields.fields.EnumIntegerField(default=0, enum=apps.shipments.models.shipment.GTXValidation),
        ),
        migrations.AddField(
            model_name='historicalshipment',
            name='gtx_validation_timestamp',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='shipment',
            name='gtx_validation',
            field=enumfields.fields.EnumIntegerField(default=0, enum=apps.shipments.models.shipment.GTXValidation),
        ),
        migrations.AddField(
            model_name='shipment',
            name='gtx_validation_timestamp',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]