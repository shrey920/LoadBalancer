from django.urls import path
from . import views

app_name = 'servers'

urlpatterns = [
    path('',views.home, name="home"),
    path('request',views.loadBalance, name="loadBalance"),
    path('request/<pk>/<duration>',views.allocateCloud, name="allocateCloud"),
]