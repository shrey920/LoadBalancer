from django.db import models

# Create your models here.

class Server(models.Model):
    name = models.CharField("Server Name",max_length=20)
    ram = models.IntegerField(default=4)
    min_ram = models.IntegerField(default=1)
    max_ram = models.IntegerField(default=16)


class Process(models.Model):
    server = models.ForeignKey(Server,related_name="server_processes",on_delete=models.CASCADE)
    expiry = models.DateTimeField(null=True)
