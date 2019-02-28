# Generated by Django 2.1.5 on 2019-02-27 16:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shipments', '0026_update_shipment_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shipment',
            name='device',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.PROTECT, to='shipments.Device'),
        ),
    ]