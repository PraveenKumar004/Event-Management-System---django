from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard),
    path('myevents/', views.myevents),
    path('account/', views.event_collection),
    path('participation/', views.participation,name='participation'),
    path('regiastration/', views.view_registration,name='regiastration'),
    path('registeredevents/', views.registerevents),
    path('downloadticket/<int:ticket_id>', views.downloadticket, name='downloadticket'),
    path('annoncewinner/events/', views.winnerselection),
    path('annoncewinner/events/<int:event_id>', views.annoncewinner),
    path('createevent/', views.create_event,name='add_questions'),
    path('dashboard/events/<int:event_id>', views.viewevent),
    path('delete/event/<int:event_id>/', views.delete_event, name='delete_event'),
    path('edit/event/<int:event_id>/', views.edit_event_view, name='edit_event'),
    path('add_to_event/<int:registration_id>/', views.add_to_event, name='add_to_event'),
    path('announce_winner/<int:event_id>/', views.announce_winner, name='announce_winner'),
    path('profile/', views.profile_view,name='profile'),
    path('logout/', views.logout),
]
