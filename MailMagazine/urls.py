from django.conf.urls import url
from .views import list_mail_magazine,create_mail_magazine,detail_mail_magazine,update_mail_magazine
app_name = "mail_magazine"

urlpatterns = [
    url(r'^$', list_mail_magazine, name="list_mail_magazine"),
    url(r'^create/$', create_mail_magazine, name="create_mail_magazine"),
    url(r'^detail/(?P<pk>[\w\-]+)/', detail_mail_magazine, name="detail_mail_magazine"),
    url(r'^(?P<pk>[\w\-]+)/update/', update_mail_magazine, name="update_mail_magazine"),
]