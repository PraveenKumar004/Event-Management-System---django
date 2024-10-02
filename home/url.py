from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('winners/', views.winner),
    path('event/register/' , views.register),
    path('event/',  views.viewevent),
]
