# Generated by Django 2.2.5 on 2019-10-29 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servers', '0006_auto_20191029_1341'),
    ]

    operations = [
        migrations.AddField(
            model_name='process',
            name='type',
            field=models.CharField(choices=[('P1', 'Process 1'), ('P2', 'Process 2'), ('P3', 'Process 3'), ('P4', 'Process 4')], default='P1', max_length=2),
        ),
    ]
