from django.urls import path
from . import views

urlpatterns =[
    path('signup/',views.signup,name='signup'),
    path('signupcollege/',views.collegesignup, name='signupcollege'),
    path('login/',views.login),
    path('signupotp/', views.generate_otp_view, name='generate_otp'),
]