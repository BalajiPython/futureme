from django.contrib import admin
from django.urls import path, include
from letters import views as letters_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', letters_views.home_view, name='home'),
    path('dashboard/', letters_views.dashboard, name='dashboard'),
    path('login/', letters_views.login_view, name='login'),
    path('register/', letters_views.register_view, name='register'),
    path('verify-otp/', letters_views.verify_otp_view, name='verify_otp_view'),
    path('api/register', letters_views.register_api, name='register_api'),
    path('api/token', letters_views.login_api, name='login_api'),
    path('api/verify-otp', letters_views.verify_otp_api, name='verify_otp_api'),
    path('write/', letters_views.write_letter, name='write_letter'),
    path('api/letters/', letters_views.api_letters, name='api_letters'),
    path('logout/', letters_views.logout_view, name='logout'),
]
