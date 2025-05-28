from django.urls import path
from . import views

urlpatterns = [
    # Regular views
    path('register/', views.register_view, name='register'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('resend-otp/', views.resend_otp_view, name='resend_otp'),
    path('delete-user/', views.delete_user_view, name='delete_user'),
    
    # API endpoints
    path('api/register/', views.register_api, name='api_register'),
    path('api/login/', views.login_api, name='api_login'),
    path('api/verify-otp/', views.verify_otp_api, name='api_verify_otp'),
    path('api/delete-user/', views.delete_user_api, name='api_delete_user'),
] 