# Generated by Django 2.0.9 on 2018-10-15 18:34

import apps.utils
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shipments', '0015_loadshipment_vault_hash'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrackingData',
            fields=[
                ('id', models.CharField(default=apps.utils.random_id, max_length=36, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('device_id', models.CharField(blank=True, max_length=36, null=True)),
                ('latitude', models.FloatField(default=None)),
                ('longitude', models.FloatField(default=None)),
                ('altitude', models.FloatField(default=None)),
                ('source', models.CharField(max_length=10)),
                ('uncertainty', models.IntegerField(blank=True, null=True)),
                ('speed', models.IntegerField(blank=True, null=True)),
                ('timestamp', models.CharField(max_length=50)),
                ('geometry', django.contrib.gis.db.models.fields.GeometryField(null=True, srid=4326)),
                ('version', models.CharField(blank=True, max_length=10, null=True)),
                ('shipment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='shipments.Shipment')),
            ],
            options={
                'ordering': ('created_at',),
            },
        ),
    ]
