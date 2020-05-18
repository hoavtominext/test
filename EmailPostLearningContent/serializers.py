from rest_framework import serializers

from .models import EmailPostContent
from django.db import IntegrityError, transaction


# normal serializer [similar to forms.Form]
class EmailPostContentSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    count_send_email = serializers.IntegerField(required=True)

    # is called if we save serializer if it do not have an instance
    def create(self, validated_data):
        results = EmailPostContent.objects.create(**validated_data)
        results.save()
        return results

    # is called if we save serializer if it have an instance
    def update(self, instance, validated_data):
        instance.user_id = validated_data.get('user_id', instance.user_id)
        instance.count_send_email = validated_data.get('count_send_email', instance.count_send_email)
        instance.save()

        return instance

    class Meta:
        unique_together = ('user_id',)
