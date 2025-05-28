from django.urls import path
from django.views.defaults import page_not_found
from . import views

handler404 = page_not_found

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp_view'),
    path('api/register', views.register_api, name='register_api'),
    path('api/token', views.login_api, name='login_api'),
    path('api/verify-otp', views.verify_otp_api, name='verify_otp_api'),
    path('write/', views.write_letter, name='write_letter'),
    path('api/letters/', views.api_letters, name='api_letters'),
    path('logout/', views.logout_view, name='logout'),
]
