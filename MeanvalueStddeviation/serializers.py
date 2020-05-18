from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.response import Response
from .models import MeanvalueStddeviation
from Answer.models import Answer
from Workshop.models import Workshop


# normal serializer [similar to forms.Form]
class MeanvalueStddeviationSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    type = serializers.CharField(max_length=100)
    average_value = serializers.FloatField()
    standard_deviation = serializers.FloatField()

    # is called if we save serializer if it do not have an instance
    def create(self, validated_data):
        meanvalue_stddeviation = MeanvalueStddeviation.objects.create(**validated_data)
        meanvalue_stddeviation.save()
        return meanvalue_stddeviation

    # is called if we save serializer if it have an instance
    def update(self, instance, validated_data):
        instance.type = validated_data.get('type', instance.type)
        instance.average_value = validated_data.get('average_value', instance.average_value)
        instance.standard_deviation = validated_data.get('standard_deviation', instance.standard_deviation)
        instance.save()

        return instance

    class Meta:
        model = MeanvalueStddeviation
        fields = ("id", "type", "average_value", "standard_deviation")
