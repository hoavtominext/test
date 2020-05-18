from rest_framework import serializers

from .models import Result, Answer
from django.db import IntegrityError, transaction


# normal serializer [similar to forms.Form]
class ResultsSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    company_id = serializers.IntegerField(required=True)
    workshop_id = serializers.IntegerField(required=True)
    count_assessment = serializers.FloatField(required=True)
    score_listen = serializers.FloatField(required=True)
    score_ask_questions = serializers.FloatField(required=True)
    score_advance = serializers.FloatField(required=True)
    score_retention = serializers.FloatField(required=True)
    score_sharing_purpose = serializers.FloatField(required=True)
    score_personal_reciprocal = serializers.FloatField(required=True)
    total_average_score = serializers.FloatField(required=True)
    total_normdist_score = serializers.FloatField(required=True)

    # is called if we save serializer if it do not have an instance
    def create(self, validated_data):
        results = Result.objects.create(**validated_data)
        results.save()
        return results

    # is called if we save serializer if it have an instance
    def update(self, instance, validated_data):
        instance.user_id = validated_data.get('user_id', instance.user_id)
        instance.workshop_id = validated_data.get('workshop_id', instance.workshop_id)
        instance.count_assessment = validated_data.get('count_assessment', instance.count_assessment)
        instance.score_listen = validated_data.get('score_listen', instance.score_listen)
        instance.score_ask_questions = validated_data.get('score_ask_questions', instance.score_ask_questions)
        instance.score_advance = validated_data.get('score_advance', instance.score_advance)
        instance.score_retention = validated_data.get('score_retention', instance.score_retention)
        instance.score_sharing_purpose = validated_data.get('score_sharing_purpose', instance.score_sharing_purpose)
        instance.score_personal_reciprocal = validated_data.get('score_personal_reciprocal',
                                                                instance.score_personal_reciprocal)
        instance.total_average_score = validated_data.get('total_average_score', instance.total_average_score)
        instance.total_normdist_score = validated_data.get('total_normdist_score', instance.total_normdist_score)
        instance.save()

        return instance

    class Meta:
        model = Result
        fields = ("id", "user_id", "question_id", "workshop_id", "count_assessment", "score_listen",
                  "score_ask_questions", "score_advance", "score_retention", "score_sharing_purpose",
                  "total_average_score", "total_normdist_score")



