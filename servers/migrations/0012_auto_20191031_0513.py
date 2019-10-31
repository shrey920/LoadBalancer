# Generated by Django 2.2.5 on 2019-10-31 05:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servers', '0011_process_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='process',
            name='sla',
            field=models.IntegerField(default=1000),
        ),
        migrations.AddField(
            model_name='process',
            name='start',
            field=models.DateTimeField(null=True),
        ),
    ]
