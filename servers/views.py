from django.shortcuts import render,redirect
from operator import attrgetter

import datetime
from datetime import timedelta

from .models import *

# Create your views here.

def home(request):

    servers = Server.objects.all()

    current_time = datetime.datetime.now()

    context = {
        "servers": [],
    }

    for server in servers:
        processes = server.server_processes.filter(expiry__gt=current_time).count()
        context['servers'].append({
            "name":server.name,
            "ram":server.ram,
            "tasks":processes
        })





    return render(request,'servers/home.html',context)



def loadBalance(request):

    duration = request.POST['duration']


    servers = Server.objects.all()
    best_server = servers[0]
    minimum = -1

    current_time = datetime.datetime.now()
    for server in servers:
        processes = server.server_processes.filter(expiry__gt=current_time).count()

        if minimum==-1 or processes<minimum:
            minimum = processes
            best_server = server


    return redirect('servers:allocateCloud', best_server.pk, duration)

def allocateCloud(request,pk, duration):

    server = Server.objects.get(pk=pk)
    process = Process()
    process.expiry = datetime.datetime.now() + timedelta(seconds=int(duration))
    process.server = server
    process.save()

    context = {
        "server": {},
    }

    current_time = datetime.datetime.now()

    processes = server.server_processes.filter(expiry__gt=current_time).count()
    context['server'] = {
        "name": server.name,
        "ram": server.ram,
        "tasks": processes
    }

    return render(request,'servers/allocated.html',context)