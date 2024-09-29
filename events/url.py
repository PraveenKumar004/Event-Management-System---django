from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard),
    path('myevents/', views.myevents),
    path('registeredevents/', views.registerevents),
]
