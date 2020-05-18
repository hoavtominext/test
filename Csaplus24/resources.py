from import_export import resources
from .models import Csaplus24Coefficient, Csaplus24Average


# from .models import UserImport

class Csaplus24CoefficientResource(resources.ModelResource):
    class Meta:
        model = Csaplus24Coefficient
        import_id_fields = ('id',)
        fields = ('id', 'name', 'category', 'type', 'factor')


class Csaplus24AverageResource(resources.ModelResource):
    class Meta:
        model = Csaplus24Average
        import_id_fields = ('id',)
        fields = ('id', 'name', 'category', 'type', 'factor')
