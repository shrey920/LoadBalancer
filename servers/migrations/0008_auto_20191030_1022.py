# Generated by Django 2.2.5 on 2019-10-30 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servers', '0007_process_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='process',
            name='ram',
            field=models.FloatField(default=0.5),
        ),
        migrations.AlterField(
            model_name='server',
            name='max_ram',
            field=models.FloatField(default=16),
        ),
        migrations.AlterField(
            model_name='server',
            name='min_ram',
            field=models.FloatField(default=1),
        ),
        migrations.AlterField(
            model_name='server',
            name='ram',
            field=models.FloatField(default=4),
        ),
    ]
