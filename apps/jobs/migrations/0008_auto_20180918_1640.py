# Generated by Django 2.0.7 on 2018-09-18 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0007_asyncjob_wallet_lock_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='asyncjob',
            name='delay',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='asyncjob',
            name='last_try',
            field=models.DateTimeField(null=True),
        ),
    ]
