from django.urls import path
from . import views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('', views.home),
    path('winners/', views.winner),
    path('event/register/<int:event_id>/' , views.register),
    path('event/<int:event_id>/',  views.viewevent,name='event_details'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
