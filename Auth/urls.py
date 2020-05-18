from django.urls import path
from . import views
urlpatterns = [
    path('login', views.login, name='login'),
    path('login-admin', views.login_admin, name='login_admin'),
    path('token/refresh', views.refresh_token, name='refresh_token'),
    path('logout', views.logout, name='logout'),
]
