from django.conf.urls import url
from .views import csaplus24_coefficient_import,csaplus24_average_import

urlpatterns = [
    url(r'^coefficient-import', csaplus24_coefficient_import, name="csaplus24_coefficient_import"),
    url(r'^average-import', csaplus24_average_import, name="csaplus24_average_import"),
]