from django.urls import path
from django.views.defaults import page_not_found
from . import views

handler404 = page_not_found

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('write/', views.write_letter, name='write_letter'),
    path('letter/<int:letter_id>/', views.view_letter, name='view_letter'),
    path('api/letters/', views.api_letters, name='api_letters'),
    path('confirmation/', views.confirmation_view, name='confirmation'),
]
