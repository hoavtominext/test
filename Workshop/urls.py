from django.conf.urls import url
from .views import workshop_list, workshop_create, workshop_edit, workshop_create_many,workshop_detail,workshop_delete

app_name = 'workshop'
urlpatterns = [
    # ex: /workshop/
    url(r'create/$', workshop_create, name="workshop_create"),
    url(r'(?P<pk>\d+)/edit/$', workshop_edit, name="workshop_edit"),
    url(r'(?P<pk>\d+)/detail/$', workshop_detail, name="workshop_detail"),
    url(r'(?P<pk>\d+)/delete/$', workshop_delete, name="workshop_delete"),
    url(r'^$', workshop_list, name="workshop_list"),
]
