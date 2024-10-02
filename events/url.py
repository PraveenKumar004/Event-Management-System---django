from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard),
    path('myevents/', views.myevents),
    path('registeredevents/', views.registerevents),
    path('dashboard/events/', views.viewevent),
    path('annoncewinner/events/', views.annoncewinner),
    path('createevent/', views.demo,name='add_questions'),
]
