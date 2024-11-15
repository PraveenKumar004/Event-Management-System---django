from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home),
    path('winners/', views.winner),
    path('event/<int:event_id>/', views.viewevent, name='event_details'),
    path('event/register/<int:event_id>/', views.register),
    path('event/register/submit/<int:event_id>/', views.register_event, name='register_event'),
    path('payment/initiate/<int:event_id>', views.initiate_payment, name='initiate_payment'),
    path('create_order/', views.create_order, name='create_order'),
    path('payment_success/', views.payment_success, name='payment_success'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
