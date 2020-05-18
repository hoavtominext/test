from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView, CreateAPIView, \
    UpdateAPIView, DestroyAPIView, get_object_or_404, GenericAPIView

from Answer.models import Result, Answer, distAnswers, SendEmailAfterCompleteQuestion
from Answer.serializers import ResultsSerializer
from Auth.views import TokenHasScopeForMethod
from Csaplus24.models import Csaplus24Average, distCsaplus24Average
from .models import Questions
from .serializers import QuestionsSerializer, AnswerQuestionsSerializer, ResultsAnswerSerializer, \
    getLastCountAssessment, average_compare_up, average_compare_down, getLastWorkshopJoin
from rest_framework.response import Response
from .resources import QuestionsResource
from tablib import Dataset
from rest_framework import status
from django.db import IntegrityError, transaction
import numpy as np
from operator import itemgetter
from collections import Counter
from Users.models import User, UserProfile
from Workshop.models import Workshop, UserWorkshop


# Create your views here.
class CheckAssessment(GenericAPIView):
    queryset = Result.objects.all()
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'GET': ['user', 'admin', 'coacha_admin']}

    def get(self, request):
        user = request.user
        assessment_count = len(self.get_queryset().filter(user_id=user.id))
        if assessment_count != 0:
            raise ValidationError('You have already completed your pre-assessment')
        else :
            return Response({'detail':'OK', 'code':200}, status=status.HTTP_200_OK)


class QuestionsList(ListCreateAPIView):
    queryset = Questions.objects.all()
    serializer_class = QuestionsSerializer
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'GET': ['user', 'admin', 'coacha_admin']}

    '''
        GET question list
    '''

    def get(self, request, *args, **kwargs):
        user = request.user
        count_assessment = len(Result.objects.filter(user_id=user.id))
        if count_assessment != 0:
            return Response({'detail': 'You have already done your pre-assessment', 'code':400}, status=status.HTTP_400_BAD_REQUEST)
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data, 'code': status.HTTP_200_OK}, status=status.HTTP_200_OK)


class QuestionsImport(CreateAPIView):
    serializer_class = QuestionsSerializer
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'POST': ['coacha_admin']}


    '''
        Import Questions
    '''

    def post(self, request, *args, **kwargs):
        try:
            questions_csv = request.FILES['questions_csv']
        except MultiValueDictKeyError:
            questions_csv = False

        Questions.objects.all().delete()

        # email = request.data['email']
        if questions_csv is False:
            data = {
                'data': {'message': 'questions_csv　ファイルが見つかりません。'},
                'code': status.HTTP_403_FORBIDDEN
            }
            return Response(data, status=status.HTTP_403_FORBIDDEN)

        user_resource = QuestionsResource()
        dataset = Dataset()

        imported_data = dataset.load(questions_csv.read().decode('utf-8'), format='csv')
        result = user_resource.import_data(dataset, dry_run=True)  # Test the data import
        if not result.has_errors():
            user_resource.import_data(dataset, dry_run=False)

        queryset = Questions.objects.all()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data, 'code': status.HTTP_200_OK}, status=status.HTTP_200_OK)


class AnswerQuestions(GenericAPIView):
    serializer_class = ResultsSerializer
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'POST': ['user','admin', 'coacha_admin']}
    '''
        POST list answer data questions
    '''

    def post(self, request, *args, **kwargs):
        answer_data = request.data
        user_id = request.data['user_id']
        user = User.objects.filter(pk=user_id).first()
        try:
            company = user.userprofile.company
            answer_data['company_id'] = company.id
        except ObjectDoesNotExist:
            return Response({"data": {'message': 'ユーザーの会社は見つかりません。'}, 'code': status.HTTP_400_BAD_REQUEST},
                            status=status.HTTP_400_BAD_REQUEST)

        workshop_id = getLastWorkshopJoin(company_id=company.id)
        serializer = ResultsAnswerSerializer(data=answer_data)
        if serializer.is_valid():
            serializer.save()

        count_assessment = getLastCountAssessment(company_id=company.id, user_id=user_id, workshop_id=workshop_id)

        queryset = Result.objects.filter(user_id=user_id, count_assessment=count_assessment,workshop_id=workshop_id,company_id=company.id)
        serializer = self.get_serializer(queryset, many=True)

        dist_answers = distAnswers(user_id, count_assessment)
        dist_csaplus24_average = distCsaplus24Average()
        data_response = {
            'radar': serializer.data,
            'average_compare_up': average_compare_up(dist_answers, dist_csaplus24_average),
            'average_compare_down': average_compare_down(dist_answers, dist_csaplus24_average)
        }
        return Response({"data": data_response, 'code': status.HTTP_200_OK}, status=status.HTTP_200_OK)


class HistoryResultAnswerQuestion(GenericAPIView):
    serializer_class = ResultsSerializer
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'GET': ['user','admin', 'coacha_admin']}
    '''
        GET get history answer data questions
    '''
    def get(self, request, *args, **kwargs):
        user = request.user
        company = user.userprofile.company
        workshop_id = getLastWorkshopJoin(company_id=company.id)
        count_assessment = getLastCountAssessment(company_id=company.id, user_id=user.id, workshop_id=workshop_id)
        queryset = Result.objects.filter(user_id=user.id, count_assessment=count_assessment, workshop_id=workshop_id,
                                         company_id=company.id)
        serializer = self.get_serializer(queryset, many=True)
        assessment_date = Answer.objects.filter(user_id=user.id, count_assessment=count_assessment,
                                                workshop_id=workshop_id)
        assessment_date = assessment_date.get(question_id=Questions.objects.all().count()).created_at
        dist_answers = distAnswers(user.id, count_assessment)
        dist_csaplus24_average = distCsaplus24Average()
        data_response = {
            'radar': serializer.data,
            'assessment_date': assessment_date.strftime("%Y年 %m月 %d日"),
            'average_compare_up': average_compare_up(dist_answers, dist_csaplus24_average),
            'average_compare_down': average_compare_down(dist_answers, dist_csaplus24_average)
        }
        return Response({"data": data_response, 'code': status.HTTP_200_OK}, status=status.HTTP_200_OK)

class SendEmailCompleteQuestion(GenericAPIView):
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'POST': ['admin', 'coacha_admin']}

    def post(self, request, *args, **kwargs):
        user = request.user
        try:
            try:
                company = user.userprofile.company
            except UserProfile.DoesNotExist:
                return Response(
                    {"data": {'message': 'company is not found  !'}, 'code': status.HTTP_400_BAD_REQUEST},
                    status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.filter(pk=user.id).first()


            try:
                workshop = Workshop.objects.filter(company_id=company.id).order_by('-date_workshop').first()
            except Workshop.DoesNotExist:
                return Response(
                    {"data": {'message': 'Workshop of company not found  !'}, 'code': status.HTTP_400_BAD_REQUEST},
                    status=status.HTTP_400_BAD_REQUEST)

            count_assessment = getLastCountAssessment(company_id=company.id, user_id=user.id, workshop_id=workshop.id)

            try:
                result = Result.objects.filter(company_id=company.id,
                                               user_id=user.id,
                                               workshop_id=workshop.id,
                                               count_assessment=count_assessment).first()
            except Result.DoesNotExist:
                return Response(
                    {"data": {'message': 'User not complete questions !'}, 'code': status.HTTP_400_BAD_REQUEST},
                    status=status.HTTP_400_BAD_REQUEST)
            # send email
            SendEmailAfterCompleteQuestion('Admin', user, result)
            return Response({"data": {'status': 'OK'}, 'code': status.HTTP_200_OK}, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response(
                {"data": {'message': 'Send mail change password errors !'}, 'code': status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST)


questions_list = QuestionsList.as_view()
questions_import = QuestionsImport.as_view()
answer_questions = AnswerQuestions.as_view()
send_email_complete_questions = SendEmailCompleteQuestion.as_view()
history_result_answer_question = HistoryResultAnswerQuestion.as_view()
pre_assessment_check = CheckAssessment.as_view()
