from django.db import models

# Create your models here.

class Server(models.Model):
    name = models.CharField("Server Name",max_length=20)
    ram = models.FloatField(default=4)
    min_ram = models.FloatField(default=1)
    max_ram = models.FloatField(default=16)


class Process(models.Model):
    PROCESS_CHOICES = [
        ('P1', 'Process 1'),
        ('P2', 'Process 2'),
        ('P3', 'Process 3'),
        ('P4', 'Process 4'),
    ]
    type = models.CharField(
        max_length=2,
        choices=PROCESS_CHOICES,
        default='P1',
    )
    server = models.ForeignKey(Server,related_name="server_processes",on_delete=models.CASCADE)
    ram = models.FloatField(null=True)
    duration = models.IntegerField(null=True)
    expiry = models.DateTimeField(null=True)
