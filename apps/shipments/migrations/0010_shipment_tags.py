# Generated by Django 2.2.7 on 2020-02-07 20:34

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('shipments', '0009_add_shipment_assignee_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShipmentTag',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('tag_type', models.CharField(max_length=50, validators=[django.core.validators.RegexValidator(message='Space(s) not allowed in this field', regex='^\\S*$')])),
                ('tag_value', models.CharField(max_length=50, validators=[django.core.validators.RegexValidator(message='Space(s) not allowed in this field', regex='^\\S*$')])),
                ('user_id',models.UUIDField(null=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('shipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shipments.Shipment', related_name='shipment_tags')),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.AddConstraint(
            model_name='shipmenttag',
            constraint=models.UniqueConstraint(fields=('tag_type', 'tag_value', 'shipment'), name='unique_tag_definition_for_shipment'),
        ),
    ]
