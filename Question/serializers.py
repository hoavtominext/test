from operator import itemgetter

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework import serializers, exceptions, status
from rest_framework.exceptions import ValidationError

from Answer.serializers import ResultsSerializer
from .models import Questions
from Users.models import User
from Answer.models import Answer, Result, scoreAnswerListen, scoreAnswerAskQuestion, totalNormdistScoreTotal, \
    totalAverageScore, scoreAnswerRetention, scoreAnswerPersonalReciprocall, scoreAnswerSharingPurpose, \
    scoreAnswerAdvance, totalNormdistScoreWithType
from Workshop.models import Workshop, UserWorkshop
from MeanvalueStddeviation import constant
from rest_framework.response import Response

# normal serializer [similar to forms.Form]
class QuestionsSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(max_length=100)
    category = serializers.CharField(max_length=100)
    type = serializers.CharField(max_length=100)
    factor = serializers.CharField(max_length=100)

    # is called if we save serializer if it do not have an instance
    def create(self, validated_data):
        questions = Questions.objects.create(**validated_data)
        questions.save()
        return questions

    # is called if we save serializer if it have an instance
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.category = validated_data.get('category', instance.category)
        instance.type = validated_data.get('type', instance.type)
        instance.factor = validated_data.get('factor', instance.factor)
        instance.save()

        return instance

    class Meta:
        model = Questions
        fields = ("id", "name", "category", "type", "type")


class AnswerQuestionsSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    question_id = serializers.IntegerField(required=True)
    company_id = serializers.IntegerField(required=True)
    point = serializers.IntegerField(required=True)
    workshop_id = serializers.IntegerField(required=False)
    count_assessment = serializers.IntegerField(required=False)

    def create(self, validated_data):
        answer = Answer.objects.create(**validated_data)
        answer.save()

        return answer

    def update(self, instance, validated_data):
        instance.user_id = validated_data.get('user_id', instance.user_id)
        instance.company_id = validated_data.get('company_id', instance.company_id)
        instance.question_id = validated_data.get('question_id', instance.question_id)
        instance.point = validated_data.get('point', instance.point)
        instance.workshop_id = validated_data.get('workshop_id', instance.workshop_id)
        instance.count_assessment = validated_data.get('count_assessment', instance.count_assessment)
        instance.save()

        return instance

    class Meta:
        model = Answer
        fields = ('user_id', 'question_id', 'point')


def increaseCountAssessment(company_id, user_id, workshop_id):
    try:
        result = Result.objects.filter(company_id=company_id, user_id=user_id, workshop_id=workshop_id).order_by(
            '-count_assessment').first()
        if result is None:
            count_assessment = 1
        else:
            count_assessment = result.count_assessment + 1
    except Result.DoesNotExist:
        count_assessment = 1

    return count_assessment


def getLastCountAssessment(company_id, user_id, workshop_id):
    try:
        result = Result.objects.filter(company_id=company_id, user_id=user_id, workshop_id=workshop_id).order_by(
            '-count_assessment').first()
        if result is None:
            count_assessment = 1
        else:
            count_assessment = result.count_assessment

    except Result.DoesNotExist:
        count_assessment = 1

    return count_assessment


def getLastWorkshopJoin(company_id):
    try:
        workshop = Workshop.objects.filter(company_id=company_id).order_by('-date_workshop').first()
    except Workshop.DoesNotExist:
        raise exceptions.ValidationError({
            'workshop': [(
                "workshop is not Exits")],
        })

    return workshop.id


class ResultsAnswerSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    answer_data = serializers.JSONField(required=True, label='answer_data')

    def create(self, validated_data):
        results = validated_data['answer_data']
        user_id = validated_data['user_id']

        user = User.objects.filter(pk=user_id).first()
        try:
            company = user.userprofile.company
        except ObjectDoesNotExist:
            raise exceptions.ValidationError({
                'user_company': [(
                    "User company is not Exits")],
            })
        try:
            with transaction.atomic():
                # save table answer
                for data in validated_data['answer_data']:
                    user_id = data['user_id']
                    question_id = data['question_id']
                    workshop_id = getLastWorkshopJoin(company_id=company.id)
                    user = User.objects.filter(pk=user_id).first()
                    company = user.userprofile.company
                    count_assessment = increaseCountAssessment(company_id=company.id, user_id=user_id,
                                                               workshop_id=workshop_id)

                    data['company_id'] = company.id
                    data['count_assessment'] = count_assessment
                    data['workshop_id'] = workshop_id
                    data['company_id'] = company.id
                    serializer = AnswerQuestionsSerializer(data=data)
                    if serializer.is_valid():
                        serializer.save()

                # save table result
                workshop_id = getLastWorkshopJoin(company_id=company.id)
                count_assessment = increaseCountAssessment(company_id=company.id, user_id=user_id,
                                                           workshop_id=workshop_id)

                score_listen = scoreAnswerListen(user_id,company.id,workshop_id, count_assessment)
                score_ask_questions = scoreAnswerAskQuestion(user_id,company.id,workshop_id, count_assessment)
                score_advance = scoreAnswerAdvance(user_id,company.id,workshop_id, count_assessment)
                score_retention = scoreAnswerRetention(user_id,company.id,workshop_id, count_assessment)
                score_sharing_purpose = scoreAnswerSharingPurpose(user_id,company.id,workshop_id, count_assessment)
                score_personal_reciprocal = scoreAnswerPersonalReciprocall(user_id,company.id,workshop_id, count_assessment)


                # check exits result
                try:
                    result = Result.objects.get(
                        user_id=user_id,
                        workshop_id=workshop_id,
                        company_id=company.id,
                        count_assessment=count_assessment,
                    )
                except Result.DoesNotExist:
                    result = None

                total_average_score = totalAverageScore(user_id,company.id,workshop_id, count_assessment, score_listen, score_ask_questions,
                                                        score_advance,
                                                        score_retention, score_sharing_purpose,
                                                        score_personal_reciprocal)
                data = {
                    'user_id': user_id,
                    'workshop_id': workshop_id,
                    'company_id': company.id,
                    'count_assessment': count_assessment,
                    'score_listen': totalNormdistScoreWithType(score_listen, constant.LISTENT),
                    'score_ask_questions': totalNormdistScoreWithType(score_ask_questions, constant.ASK_QUESTION),
                    'score_advance': totalNormdistScoreWithType(score_advance, constant.ADVANCE),
                    'score_retention': totalNormdistScoreWithType(score_retention, constant.RETENTION),
                    'score_sharing_purpose': totalNormdistScoreWithType(score_sharing_purpose,
                                                                        constant.SHARING_PURPOSE),
                    'score_personal_reciprocal': totalNormdistScoreWithType(score_personal_reciprocal,
                                                                            constant.PERSONAL_RECIPROCAL),
                    'total_average_score': total_average_score,
                    'total_normdist_score': totalNormdistScoreTotal(total_average_score),
                }

                if result:
                    serializerResults = ResultsSerializer(result, data=data)
                else:
                    try:
                        user_workshop = UserWorkshop.objects.filter(user_id=user_id, workshop_id=workshop_id,company_id=company.id).first()
                    except UserWorkshop.DoesNotExist:
                        user_workshop = None

                    if user_workshop is not None:
                        user_workshop.completed_assessment = True
                        user_workshop.save()
                    else:
                        user_workshop = UserWorkshop.objects.create(
                            user_id=user_id,
                            workshop_id=workshop_id,
                            company_id=company.id,
                            completed_assessment=True
                        )
                        user_workshop.save()

                    serializerResults = ResultsSerializer(data=data)

                if serializerResults.is_valid():
                    serializerResults.save()

        except IndentationError:
            transaction.set_rollback(True)
            raise exceptions.ValidationError({
                '500': [(
                    "500 Errors")],
            })

        return results

    # is called if we save serializer if it have an instance
    def update(self, instance, validated_data):
        return instance


def average_compare_up(dist_answers, dist_Csaplus24Average):
    average_compare = []
    for answer in dist_answers:
        for average in dist_Csaplus24Average:
            if answer['id'] == average['id']:
                factor = float(answer['factor']) - float(average['factor'])
                data = {
                    'id': answer['id'],
                    'factor': factor,
                    'name': average['name']
                }
                if factor > 0:
                    average_compare.append(data)

    average_compare_up = sorted(average_compare, key=itemgetter('factor'), reverse=True)[:3]

    return average_compare_up


def average_compare_down(dist_answers, dist_Csaplus24Average):
    average_compare = []
    for answer in dist_answers:
        for average in dist_Csaplus24Average:
            if answer['id'] == average['id']:
                factor = float(answer['factor']) - float(average['factor'])
                data = {
                    'id': answer['id'],
                    'factor': factor,
                    'name': average['name']
                }
                if factor < 0:
                    average_compare.append(data)

    average_compare_up = sorted(average_compare, key=itemgetter('factor'), reverse=False)[:3]

    return average_compare_up
