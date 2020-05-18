from rest_framework import serializers

from .models import Department
from django.db import IntegrityError, transaction


# normal serializer [similar to forms.Form]
class DeparmentListSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True)
    created_at = serializers.DateTimeField(required=False)
    updated_at = serializers.DateTimeField(required=False)
