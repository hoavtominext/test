from import_export import resources
from .models import Questions


# from .models import UserImport

class QuestionsResource(resources.ModelResource):
    class Meta:
        model = Questions
        import_id_fields = ('id',)
        fields = ('id','name', 'category', 'type', 'factor')
