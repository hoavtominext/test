from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.response import Response
from .models import Csaplus24Average, Csaplus24Coefficient
from Question.models import Questions

# normal serializer [similar to forms.Form]
class Csaplus24AverageSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    name = serializers.CharField(max_length=100)
    category = serializers.CharField(max_length=100)
    type = serializers.CharField(max_length=100)
    factor = serializers.CharField(max_length=100)

    # is called if we save serializer if it do not have an instance
    def create(self, validated_data):
        csaplus24_average = Csaplus24Average.objects.create(**validated_data)
        csaplus24_average.save()
        return csaplus24_average

    # is called if we save serializer if it have an instance
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.category = validated_data.get('category', instance.category)
        instance.type = validated_data.get('type', instance.type)
        instance.factor = validated_data.get('factor', instance.factor)
        instance.save()

        return instance

    class Meta:
        model = Csaplus24Average
        fields = ("id", "name", "category", "type", "type")


# normal serializer [similar to forms.Form]
class Csaplus24CoefficientSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    name = serializers.CharField(max_length=100)
    category = serializers.CharField(max_length=100)
    type = serializers.CharField(max_length=100)
    factor = serializers.CharField(max_length=100)

    # is called if we save serializer if it do not have an instance
    def create(self, validated_data):
        csaplus24_coefficient = Csaplus24Coefficient.objects.create(**validated_data)
        csaplus24_coefficient.save()
        return csaplus24_coefficient

    # is called if we save serializer if it have an instance
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.category = validated_data.get('category', instance.category)
        instance.type = validated_data.get('type', instance.type)
        instance.factor = validated_data.get('factor', instance.factor)
        instance.save()

        return instance

    class Meta:
        model = Csaplus24Coefficient
        fields = ("id", "name", "category", "type", "type")
