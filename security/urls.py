from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('security_events/', views.security_events, name='security_events'),

    path('register/', views.register, name='register'),
    path('register/totp_setup/', views.totp_setup, name='totp_setup'),
    path('register/facerec_setup/', views.FaceRecSetup.as_view(), name='facerec_setup'),
    path('register/capture_photo/', views.FaceRecSetup.capturePhoto, name='capture_photo'),

    path('login_password/', views.login_password, name='login_password'),
    path('login_totp/', views.login_totp, name='login_totp'),
    path('login_facerec/', views.login_facerec, name='login_facerec'),
]