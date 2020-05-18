from django.conf.urls import url
from .views import company_create,company_list,company_edit,company_detail,company_delete
app_name = "company"

urlpatterns = [
    url(r'^$', company_list, name="company_list"),
    url(r'create/$', company_create, name="company_create"),
    url(r'(?P<pk>\d+)/edit/$', company_edit, name="company_edit"),
    url(r'(?P<pk>\d+)/detail/$', company_detail, name="company_detail"),
    url(r'(?P<pk>\d+)/delete/$', company_delete, name="company_delete"),
]