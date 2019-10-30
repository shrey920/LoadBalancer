from django.shortcuts import render,redirect
from django.db.models import Q
from django.views.generic.edit import CreateView

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

        run_processes = server.server_processes.filter(expiry__gt=current_time)

        wait_processes = server.server_processes.filter(expiry__isnull=True).count()
        # ram = max(0, server.ram - run_processes)
        ram_used = sum(process.ram for process in run_processes)


        context['servers'].append({
            "pk":server.pk,
            "name":server.name,
            "ram":server.ram - ram_used,
            "run_processes":run_processes.count(),
            "wait_processes": wait_processes
        })





    return render(request,'servers/home.html',context)




class ProcessCreate(CreateView):
    model = Process
    fields = ['type']
    template_name = 'servers/createProcess.html'


    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save(commit=False)


        servers = Server.objects.all()
        best_server = servers[0]
        minimum = -1

        current_time = datetime.datetime.now()
        for server in servers:
            processes = server.server_processes.filter(Q(expiry__gt=current_time) | Q(expiry__isnull=True)).count()

            if minimum == -1 or processes < minimum:
                minimum = processes
                best_server = server

        self.object.server = best_server
        self.object.save()
        server = best_server

        ram = 0
        while ram <= 0:
            current_time = datetime.datetime.now()
            processes = server.server_processes.filter(Q(expiry__gt=current_time) | Q(expiry__isnull=True)).count() - 1
            ram = max(0, server.ram - processes)


        duration = 0

        if self.object.type == 'P1':
            self.object.ram = 0.25
            duration = 10
        if self.object.type == 'P2':
            self.object.ram = 0.5
            duration = 25
        if self.object.type == 'P3':
            self.object.ram = 0.75
            duration = 50
        if self.object.type == 'P4':
            self.object.ram = 1.0
            duration = 100

        self.object.expiry = datetime.datetime.now() + timedelta(seconds=int(duration))
        self.object.save()

        context = {
            "server": {},
        }

        current_time = datetime.datetime.now()

        run_processes = server.server_processes.filter(expiry__gt=current_time)

        ram_used = sum(process.ram for process in run_processes)

        # ram = max(0, server.ram - run_processes)
        wait_processes = server.server_processes.filter(expiry__isnull=True).count()

        context['server'] = {
            "name": server.name,
            "ram": server.ram - ram_used,
            "run_processes": run_processes.count(),
            "wait_processes": wait_processes
        }

        return render(self.request, 'servers/allocated.html', context)




def scaleUp(request, pk):

    server = Server.objects.get(pk=pk)
    if server.ram < server.max_ram:
        server.ram = server.ram + 1
        server.save()



    return redirect('servers:home')

def scaleDown(request, pk):

    server = Server.objects.get(pk=pk)
    if server.ram > server.min_ram:
        server.ram = server.ram - 1
        server.save()



    return redirect('servers:home')




def loadBalance(request):

    duration = request.POST['duration']


    servers = Server.objects.all()
    best_server = servers[0]
    minimum = -1

    current_time = datetime.datetime.now()
    for server in servers:
        processes = server.server_processes.filter(Q(expiry__gt=current_time) | Q(expiry__isnull=True)).count()

        if minimum==-1 or processes<minimum:
            minimum = processes
            best_server = server




    return redirect('servers:allocateCloud', best_server.pk, duration)

def allocateCloud(request,pk, duration):

    server = Server.objects.get(pk=pk)

    process = Process()
    process.server = server
    process.save()

    ram = 0
    while ram <= 0:
        current_time = datetime.datetime.now()
        processes = server.server_processes.filter(Q(expiry__gt=current_time) | Q(expiry__isnull=True)).count() - 1
        ram = max(0, server.ram - processes)

    process.expiry = datetime.datetime.now() + timedelta(seconds=int(duration))
    process.save()


    context = {
        "server": {},
    }

    current_time = datetime.datetime.now()

    run_processes = server.server_processes.filter(expiry__gt=current_time).count()

    ram = max(0, server.ram - run_processes)
    wait_processes = server.server_processes.filter(expiry__isnull=True).count()



    context['server'] = {
        "name": server.name,
        "ram": ram,
        "run_processes": run_processes,
        "wait_processes": wait_processes
    }

    return render(request,'servers/allocated.html',context)