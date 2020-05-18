from django.conf.urls import url
from .models import Department
from .views import department_list
app_name = "department"

urlpatterns = [
    url(r'^$', department_list, name="department_list"),
]