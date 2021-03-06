from django.shortcuts import render,redirect
from django.db.models import Q
from django.views.generic.edit import CreateView
from django.utils import timezone
import datetime
from datetime import timedelta

from .models import *

rrindex = 0

# Create your views here.


def home(request):

    servers = Server.objects.all()

    current_time = timezone.now()

    context = {
        "servers": [],
    }

    for server in servers:

        run_processes = server.server_processes.filter(expiry__gt=current_time)

        wait_processes = server.server_processes.filter(expiry__isnull=True).count()
        # ram = max(0, server.ram - run_processes)
        ram_used = sum(process.ram for process in run_processes)

        if server.ram<server.max_ram and wait_processes>0 and server.ram - ram_used < 1:
            server.ram = server.ram * 2
            server.save()
        elif ram_used<server.ram/2 and server.ram!=server.min_ram:
            server.ram = server.ram / 2
            server.save()


        context['servers'].append({
            "pk":server.pk,
            "name":server.name,
            "ram_used": ram_used,
            "ram": server.ram,
            "run_processes":run_processes.count(),
            "wait_processes": wait_processes
        })





    return render(request,'servers/home.html',context)




class LeastConnections(CreateView):
    model = Process
    fields = ['type', 'sla']
    template_name = 'servers/createProcess.html'

    def render_to_response(self, context, **response_kwargs):
        """
        Return a response, using the `response_class` for this view, with a
        template rendered with the given context.
        Pass response_kwargs to the constructor of the response class.
        """
        response_kwargs.setdefault('content_type', self.content_type)
        context['title']="Least Connections"
        return self.response_class(
            request=self.request,
            template=self.get_template_names(),
            context=context,
            using=self.template_engine,
            **response_kwargs
        )


    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save(commit=False)
        self.object.end = timezone.now() + timedelta(seconds=self.object.sla)

        servers = Server.objects.all()
        best_server = servers[0]
        minimum = -1

        current_time = timezone.now()
        for server in servers:
            processes = server.server_processes.filter(Q(expiry__gt=current_time) | Q(expiry__isnull=True)).count()

            if minimum == -1 or processes < minimum:
                minimum = processes
                best_server = server

        self.object.server = best_server
        self.object.save()

        process = Process.objects.get(pk=self.object.pk)

        if process.type == 'P1':
            process.ram = 0.25
            process.duration = 10
        if process.type == 'P2':
            process.ram = 0.5
            process.duration = 25
        if process.type == 'P3':
            process.ram = 0.75
            process.duration = 50
        if process.type == 'P4':
            process.ram = 1.0
            process.duration = 100

        server = Server.objects.get(pk=best_server.pk)
        current_time = timezone.now()
        run_processes = server.server_processes.filter(expiry__gt=current_time)
        ram_used = sum(process.ram for process in run_processes)

        ram = server.ram - ram_used


        while ram < process.ram:
            server = Server.objects.get(pk=best_server.pk)
            current_time = timezone.now()

            if process.end > current_time + timedelta(seconds=process.duration):
                swap_process_pool = server.server_processes.filter(expiry__gt=current_time, end__gt=process.end).order_by('-end')
                if swap_process_pool.count()>0:
                    swap_process = swap_process_pool[0]
                    process.expiry = timezone.now() + timedelta(seconds=process.duration)
                    process.save()
                    process = swap_process
                    process.expiry = None
                    process.save()


            run_processes = server.server_processes.filter(expiry__gt=current_time)
            ram_used = sum(process.ram for process in run_processes)

            ram = server.ram - ram_used





        process.expiry = timezone.now() + timedelta(seconds=process.duration)
        process.save()

        context = {
            "server": {},
        }

        current_time = timezone.now()

        run_processes = server.server_processes.filter(expiry__gt=current_time)

        ram_used = sum(process.ram for process in run_processes)

        # ram = max(0, server.ram - run_processes)
        wait_processes = server.server_processes.filter(expiry__isnull=True).count()


        context['server'] = {
            "name": server.name,
            "ram_used": ram_used,
            "ram": server.ram,
            "run_processes": run_processes.count(),
            "wait_processes": wait_processes
        }

        return render(self.request, 'servers/allocated.html', context)



class RoundRobin(CreateView):
    model = Process
    fields = ['type', 'sla']
    template_name = 'servers/createProcess.html'

    def render_to_response(self, context, **response_kwargs):
        """
        Return a response, using the `response_class` for this view, with a
        template rendered with the given context.
        Pass response_kwargs to the constructor of the response class.
        """
        response_kwargs.setdefault('content_type', self.content_type)
        context['title']="Round Robin"
        return self.response_class(
            request=self.request,
            template=self.get_template_names(),
            context=context,
            using=self.template_engine,
            **response_kwargs
        )


    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save(commit=False)
        self.object.end = timezone.now() + timedelta(seconds=self.object.sla)

        servers = Server.objects.all()

        global rrindex
        best_server = servers[rrindex]
        rrindex = (rrindex+1)%(servers.count())

        self.object.server = best_server
        self.object.save()

        process = Process.objects.get(pk=self.object.pk)

        if process.type == 'P1':
            process.ram = 0.25
            process.duration = 10
        if process.type == 'P2':
            process.ram = 0.5
            process.duration = 25
        if process.type == 'P3':
            process.ram = 0.75
            process.duration = 50
        if process.type == 'P4':
            process.ram = 1.0
            process.duration = 100

        server = Server.objects.get(pk=best_server.pk)
        current_time = timezone.now()
        run_processes = server.server_processes.filter(expiry__gt=current_time)
        ram_used = sum(process.ram for process in run_processes)

        ram = server.ram - ram_used

        while ram < process.ram:
            server = Server.objects.get(pk=best_server.pk)
            current_time = timezone.now()

            if process.end > current_time + timedelta(seconds=process.duration):
                swap_process_pool = server.server_processes.filter(expiry__gt=current_time,
                                                                   end__gt=process.end).order_by('-end')
                if swap_process_pool.count() > 0:
                    swap_process = swap_process_pool[0]
                    process.expiry = timezone.now() + timedelta(seconds=process.duration)
                    process.save()
                    process = swap_process
                    process.expiry = None
                    process.save()

            run_processes = server.server_processes.filter(expiry__gt=current_time)
            ram_used = sum(process.ram for process in run_processes)

            ram = server.ram - ram_used

        process.expiry = timezone.now() + timedelta(seconds=process.duration)
        process.save()

        context = {
            "server": {},
        }

        current_time = timezone.now()

        run_processes = server.server_processes.filter(expiry__gt=current_time)

        ram_used = sum(process.ram for process in run_processes)

        # ram = max(0, server.ram - run_processes)
        wait_processes = server.server_processes.filter(expiry__isnull=True).count()

        context['server'] = {
            "name": server.name,
            "ram_used": ram_used,
            "ram": server.ram,
            "run_processes": run_processes.count(),
            "wait_processes": wait_processes
        }

        return render(self.request, 'servers/allocated.html', context)


def scaleUp(request, pk):

    server = Server.objects.get(pk=pk)
    if server.ram < server.max_ram:
        server.ram = server.ram * 2
        server.save()



    return redirect('servers:home')

def scaleDown(request, pk):

    server = Server.objects.get(pk=pk)
    if server.ram > server.min_ram:
        server.ram = server.ram / 2
        server.save()



    return redirect('servers:home')




def loadBalance(request):

    duration = request.POST['duration']


    servers = Server.objects.all()
    best_server = servers[0]
    minimum = -1

    current_time = timezone.now()
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
        current_time = timezone.now()
        processes = server.server_processes.filter(Q(expiry__gt=current_time) | Q(expiry__isnull=True)).count() - 1
        ram = max(0, server.ram - processes)

    process.expiry = timezone.now() + timedelta(seconds=int(duration))
    process.save()


    context = {
        "server": {},
    }

    current_time = timezone.now()

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