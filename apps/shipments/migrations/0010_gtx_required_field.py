# Generated by Django 2.2.7 on 2020-03-03 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipments', '0009_add_shipment_assignee_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalshipment',
            name='gtx_required',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='shipment',
            name='gtx_required',
            field=models.BooleanField(default=False),
        ),
    ]