from django.urls import path
from . import views

app_name = 'servers'

urlpatterns = [
    path('',views.home, name="home"),


    path('request',views.loadBalance, name="loadBalance"),
    path('request/<pk>/<duration>',views.allocateCloud, name="allocateCloud"),


    path('scaleup/<pk>', views.scaleUp, name="scaleUp"),
    path('scaledown/<pk>', views.scaleDown, name="scaleDown"),


    path('leastConnections', views.LeastConnections.as_view(), name="leastConnections"),
    path('roundRobin', views.RoundRobin.as_view(), name="roundRobin"),

]