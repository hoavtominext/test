"""DjangoRestApi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os

from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django.conf.urls.static import static
import oauth2_provider.views as oauth2_views
from django.conf import settings
from oauth2_provider.urls import app_name
from rest_framework_swagger.views import get_swagger_view

# OAuth2 provider endpoints
oauth2_endpoint_views = [
    url(r'^authorize/$', oauth2_views.AuthorizationView.as_view(), name="authorize"),
    url(r'^token/$', oauth2_views.TokenView.as_view(), name="token"),
    url(r'^revoke-token/$', oauth2_views.RevokeTokenView.as_view(), name="revoke-token"),
]

if settings.DEBUG:
    # OAuth2 Application Management endpoints
    oauth2_endpoint_views += [
        url(r'^applications/$', oauth2_views.ApplicationList.as_view(), name="list"),
        url(r'^applications/register/$', oauth2_views.ApplicationRegistration.as_view(), name="register"),
        url(r'^applications/(?P<pk>\d+)/$', oauth2_views.ApplicationDetail.as_view(), name="detail"),
        url(r'^applications/(?P<pk>\d+)/delete/$', oauth2_views.ApplicationDelete.as_view(), name="delete"),
        url(r'^applications/(?P<pk>\d+)/update/$', oauth2_views.ApplicationUpdate.as_view(), name="update"),
    ]

    # OAuth2 Token Management endpoints
    oauth2_endpoint_views += [
        url(r'^authorized-tokens/$', oauth2_views.AuthorizedTokensListView.as_view(), name="authorized-token-list"),
        url(r'^authorized-tokens/(?P<pk>\d+)/delete/$', oauth2_views.AuthorizedTokenDeleteView.as_view(),
            name="authorized-token-delete"),
    ]
schema_view = get_swagger_view(title='API')

urlpatterns = [
    url('^accounts/', admin.site.urls),
    url(r'^$', schema_view),
    url(r'^o/', include((oauth2_endpoint_views, app_name), namespace="oauth2_provider")),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    path('v1/django-forgot-password/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    # path('v1/forgot-password/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('v1/auth/', include('Auth.urls'), name="Auth"),
    path('v1/users/', include('Users.urls'), name='users'),
    path('v1/questions/', include('Question.urls'), name='questions'),
    path('v1/workshop/', include('Workshop.urls'), name='workshop'),
    path('v1/csaplus24/', include('Csaplus24.urls'), name='csaplus24'),
    path('v1/meanvalue-stddeviation/', include('MeanvalueStddeviation.urls'), name='meanvalueStddeviation'),
    path('v1/department/', include('Department.urls'), name='Department'),
    path('v1/company/', include('Company.urls'), name='Company'),
    path('v1/mail-magazine/', include('MailMagazine.urls'), name='MailMagazine'),
    path('v1/schedule-cron/', include('ScheduleCron.urls'), name='ScheduleCron'),
    path('health/', include('health_check.urls')),
]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
