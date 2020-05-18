from django.conf.urls import url
from .views import meanvalue_stddeviation_import

urlpatterns = [
    url(r'^import-csv', meanvalue_stddeviation_import, name="meanvalue_stddeviation_import"),

]
