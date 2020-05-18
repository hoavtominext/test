from import_export import resources
from .models import MeanvalueStddeviation


# from .models import UserImport

class MeanvalueStddeviationResource(resources.ModelResource):
    class Meta:
        model = MeanvalueStddeviation
        import_id_fields = ('id',)
        fields = ('id','type', 'average_value', 'standard_deviation')
