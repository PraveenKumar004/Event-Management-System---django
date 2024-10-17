from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard),
    path('myevents/', views.myevents),
    path('registeredevents/', views.registerevents),
    path('annoncewinner/events/', views.annoncewinner),
    path('createevent/', views.create_event,name='add_questions'),
    path('dashboard/events/<int:event_id>', views.viewevent),
    path('delete/event/<int:event_id>/', views.delete_event, name='delete_event'),
    path('edit/event/<int:event_id>/', views.edit_event_view, name='edit_event'),
]
