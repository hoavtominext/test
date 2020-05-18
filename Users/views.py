import codecs
from datetime import date
from functools import reduce
from time import localtime
from django.core.validators import validate_email
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.utils.translation import activate
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView, CreateAPIView, \
    UpdateAPIView, DestroyAPIView, get_object_or_404, GenericAPIView
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination

from Auth.views import API_ENDPOINT, IPCheck
from Company.models import Company
from Question.serializers import getLastWorkshopJoin
from Users.models import User
import tablib
import requests
from Workshop.models import UserWorkshop, Workshop
from .parser import CsvParser
from .serializers import UserSerializer, ChangePasswordSerializer, UserUpdateSerializer, ImportUserSerializer, \
    ListUserAdminSerializer, SendEmailWhenCreatedUser, SettingSendEmailUserSerializer, ForgotPasswordRequestSerializer, \
    ForgotPasswordConfirmSerializer, SendEmailRequestUserWorkshop,create_token
from rest_framework.response import Response
from rest_framework import status
from tablib import Dataset
from rest_framework.permissions import IsAuthenticated
from .models import UserProfile
from import_export import resources
import csv, io
import datetime
import re
import random
import string
from Department.models import Department
from Auth.views import TokenHasScopeForMethod
from django_rest_passwordreset.models import ResetPasswordToken
from Auth.views import  user_login

from django.contrib.auth.models import Group
import operator
from django.core.exceptions import ValidationError
from rest_framework import serializers, exceptions, status
import datetime
from django.db.models import F


class UserPagination(LimitOffsetPagination, PageNumberPagination):
    default_limit = 20


class UsersList(ListCreateAPIView, LimitOffsetPagination):
    serializer_class = ListUserAdminSerializer
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'GET': ['admin', 'coacha_admin']}
    pagination_class = UserPagination

    def get_queryset(self):
        company_id = self.request.GET['company_id']
        if company_id is None:
            try:
                user_admin = self.request.user
                company = user_admin.userprofile.company
                company_id = company.id
            except User.DoesNotExist:
                return Response({"data": {
                    'message': 'ユーザーadminの会社が見つかりません'
                }, 'code': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)


        instance = self.request.user
        user_scope = str(instance.groups.first())
        if user_scope == 'admin':
            if int(instance.userprofile.company_id) != int(company_id):
                raise PermissionDenied('権限がありません')

        search = self.request.query_params.get('search', None)
        department = self.request.query_params.get('department', None)
        is_active = self.request.query_params.get('is_active', None)
        assessment = self.request.query_params.get('assessment', None)
        workshop = self.request.query_params.get('workshop', None)
        q_objects = Q()  # Create an empty Q object to start with
        if search is not None and search != '':
            q_objects |= Q(last_name__contains=search)
            q_objects |= Q(first_name__contains=search)
            q_objects |= Q(email__contains=search)
            q_objects |= Q(userprofile__department__contains=search)

        if is_active is not None and search != '':
            q_objects &= Q(is_active=is_active)
        if department is not None and search != '':
            q_objects &= Q(userprofile__department__contains=department)
        if assessment == '1':
            q_objects &= Q(userworkshop__completed_assessment=assessment)
            q_objects &= Q(userworkshop__workshop_id__isnull=False)
        if assessment == '0':
            User.objects.filter(userworkshop__completed_assessment__isnull=True)
            q_objects &= (Q(userworkshop__completed_assessment__isnull=True)|Q(userworkshop__completed_assessment=False))

        if workshop is not None and search != '':
            q_objects &= Q(userworkshop__workshop__code=workshop)

        q_objects &= Q(userprofile__company_id__exact=company_id)
        q_objects &= Q(groups__name__in=['admin','user'])
        queryset = User.objects.filter(q_objects)

        #Sort
        _status = self.request.query_params.get('sort_status', -1)
        _employee_id = self.request.query_params.get('sort_employee_id', -1)
        _is_admin = self.request.query_params.get('sort_is_admin', -1)
        _last_name = self.request.query_params.get('sort_last_name', -1)
        _email = self.request.query_params.get('sort_email', -1)
        _date_workshop = self.request.query_params.get('sort_date_workshop', -1)
        _assessment = self.request.query_params.get('sort_assessment', -1)
        _is_send_mail_magazine = self.request.query_params.get('sort_mail_magazine', -1)
        _last_login = self.request.query_params.get('sort_last_login', -1)
        _position_department = self.request.query_params.get('sort_position_department', -1)
        _department = self.request.query_params.get('sort_department', -1)

        if int(_status) == 1:
            queryset = queryset.order_by('-is_active')
        elif int(_status) == 0:
            queryset = queryset.order_by('is_active')

        elif int(_employee_id) == 1:
            queryset = queryset.distinct('id', 'userprofile__employee_id')
            queryset = queryset.order_by('-userprofile__employee_id')
        elif int(_employee_id) == 0:
            queryset = queryset.distinct('id', 'userprofile__employee_id')
            queryset = queryset.order_by('userprofile__employee_id')

        elif int(_is_admin) == 1:
            queryset = queryset.distinct('id','groups__name')
            queryset = queryset.order_by('-groups__name')
        elif int(_is_admin) == 0:
            queryset = queryset.distinct('id','groups__name')
            queryset = queryset.order_by('groups__name')

        elif int(_last_name) == 1:
            queryset = queryset.order_by('-last_name','-first_name')
        elif int(_last_name) == 0:
            queryset = queryset.order_by('last_name','first_name')

        elif int(_email) == 1:
            queryset = queryset.order_by('-email')
        elif int(_email) == 0:
            queryset = queryset.order_by('email')

        elif int(_date_workshop) == 1:
            queryset = queryset.distinct('id', 'userworkshop__workshop__date_workshop')
            queryset = queryset.order_by('-userworkshop__workshop__date_workshop')
        elif int(_date_workshop) == 0:
            queryset = queryset.distinct('id', 'userworkshop__workshop__date_workshop')
            queryset = queryset.order_by('userworkshop__workshop__date_workshop')

        elif int(_assessment) == 1:
            queryset = queryset.distinct('id', 'userworkshop__completed_assessment')
            queryset = queryset.order_by(F('userworkshop__completed_assessment').desc(nulls_last=True))
        elif int(_assessment) == 0:
            queryset = queryset.distinct('id', 'userworkshop__completed_assessment')
            queryset = queryset.order_by(F('userworkshop__completed_assessment').asc(nulls_first=True))

        elif int(_is_send_mail_magazine) == 1:
            queryset = queryset.distinct('id', 'userprofile__is_send_email')
            queryset = queryset.order_by('-userprofile__is_send_email')
        elif int(_is_send_mail_magazine) == 0:
            queryset = queryset.distinct('id', 'userprofile__is_send_email')
            queryset = queryset.order_by('userprofile__is_send_email')

        elif int(_last_login) == 1:
            queryset = queryset.distinct('id', 'last_login')
            queryset = queryset.order_by(F('last_login').desc(nulls_last=True))
        elif int(_last_login) == 0:
            queryset = queryset.distinct('id', 'last_login')
            queryset = queryset.order_by(F('last_login').asc(nulls_first=True))

        elif int(_position_department) == 1:
            queryset = queryset.distinct('id', 'userprofile__position_department')
            queryset = queryset.order_by('-userprofile__position_department')
        elif int(_position_department) == 0:
            queryset = queryset.distinct('id', 'userprofile__position_department')
            queryset = queryset.order_by('userprofile__position_department')

        elif int(_department) == 1:
            queryset = queryset.distinct('id', 'userprofile__department')
            queryset = queryset.order_by('-userprofile__department')
        elif int(_department) == 0:
            queryset = queryset.distinct('id', 'userprofile__department')
            queryset = queryset.order_by('userprofile__department')

        else:
            queryset = queryset.distinct('id')
            queryset = queryset

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data, 'code': 200})



class UserCreate(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'POST': ['admin', 'coacha_admin']}

    def post(self, request, *args, **kwargs):
        user_scope = str(request.user.groups.first())
        company_id = kwargs.get('company_id')
        if company_id is None :
            company_id = request.user.userprofile.company_id
        context = {"company_id": company_id}
        serializer = UserSerializer(data=request.data, context=context)

        if serializer.is_valid() :
            serializer.save()
            queryset = User.objects.all().order_by('-id')
            serializer = ListUserAdminSerializer(queryset, many=True)
            return Response({"data": serializer.data, 'code': 200}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_200_OK)


class UserUpdate(UpdateAPIView):
    serializer_class = UserSerializer
    model = User
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'PUT': ['admin', 'coacha_admin']}

    def get_object(self, queryset=None):
        obj = User.objects.filter(pk=self.kwargs.get('pk')).first()
        return obj

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data)

        if serializer.is_valid() :
            serializer.save()
            queryset = User.objects.all().order_by('-id')
            serializer = ListUserAdminSerializer(queryset, many=True)
            return Response({"data": serializer.data, 'code': 200}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_200_OK)


class UserDelete(DestroyAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'DELETE': ['admin', 'coacha_admin']}

    def delete(self, request, *args, **kwargs):
        user_scope = str(request.user.groups.first())
        instance = self.get_object()

        if user_scope == 'admin' and instance.userprofile.company_id != request.user.userprofile.company_id :
            raise PermissionDenied('ユーザーを削除する権限がありません')

        if instance.is_superuser is True:
            data = {
                'data': {'message': '管理者のユーザーを削除できません'},
                'code': status.HTTP_403_FORBIDDEN
            }
            return Response(data, status=status.HTTP_403_FORBIDDEN)
        else:
            self.perform_destroy(instance)
            data = {
                'data': {'message': 'ユーザーを削除しました'},
                'code': status.HTTP_200_OK
            }

        return Response(data, status=status.HTTP_200_OK)

def randomStringDigits(stringLength = 8):
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))

class UserImport(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'POST': ['admin', 'coacha_admin']}
    admin_group = Group.objects.get(name='admin')
    user_group = Group.objects.get(name='user')

    def post(self, request, *args, **kwargs):
        user_admin = request.user
        company_id = request.POST.get('company_id')
        if company_id is None:
            company_id = user_admin.userprofile.company.id

        try:
            company = Company.objects.get(pk=company_id)
            users_csv = request.FILES.get('user_csv')

            # let's check if it is a csv file
            if not users_csv.name.endswith('.csv'):
                return Response({"detail": ["データ形式が不正です"], 'code': status.HTTP_400_BAD_REQUEST, },
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                data_set = users_csv.read().decode('utf-8')
            except UnicodeDecodeError:
                return Response({"detail": ["文字コードが違います。UTF-8形式に変換の上アップロードしてください"], 'code': status.HTTP_400_BAD_REQUEST, },
                                status=status.HTTP_400_BAD_REQUEST)

            # setup a stream which is when we loop through each line we are able to handle a data in a stream
            io_string = io.StringIO(data_set)
            next(io_string)
            for column in csv.reader(io_string, delimiter=',', quotechar="|"):
                if len(column) == 0:
                    break
                employee_id = column[0]
                last_name = column[1]
                first_name = column[2]
                last_furigana = column[3]
                first_furigana = column[4]
                email = column[5].lower()
                birthday = column[6]
                sex = column[7]
                job_position = column[8]
                department = column[9]
                date_joined = column[10]
                workshop_code = column[11]
                email_magazine = column[12]
                is_admin = column[13]

                if last_name == '' or first_name == '' or email == '':
                    return Response({"detail": ["未入力の必須項目があります"], 'code': status.HTTP_400_BAD_REQUEST, },
                                    status=status.HTTP_400_BAD_REQUEST)

                if birthday != '':
                    try:
                        d = datetime.datetime.strptime(birthday, '%Y-%m-%d')
                        birthday = d.strftime('%Y-%m-%d')
                    except ValueError:
                        try:
                            d = datetime.datetime.strptime(birthday, '%Y/%m/%d')
                            birthday = d.strftime('%Y-%m-%d')
                        except:
                            return Response({"detail": ["生年月日のデータ形式が不正または存在しない日付です <br/> yyyy/mm/ddで入力してください"], 'code': status.HTTP_400_BAD_REQUEST, },
                                        status=status.HTTP_400_BAD_REQUEST)

                else:
                    birthday=None

                if date_joined != '':
                    try:
                        d = datetime.datetime.strptime(date_joined, '%Y-%m-%d')
                        date_joined = d.strftime('%Y-%m-%d')
                    except ValueError:
                        try:
                            d = datetime.datetime.strptime(date_joined, '%Y/%m/%d')
                            date_joined = d.strftime('%Y-%m-%d')
                        except:
                            return Response({"detail": ["入社月のデータ形式が不正または存在しない日付です <br/> yyyy/mm/ddで入力してください"], 'code': status.HTTP_400_BAD_REQUEST, },
                                        status=status.HTTP_400_BAD_REQUEST)

                else:
                    date_joined = None

                try:
                    validate_email(email)
                except ValidationError:
                    return Response({"detail": ["メールアドレスのデータ形式が不正です"], 'code': status.HTTP_400_BAD_REQUEST, },
                                    status=status.HTTP_400_BAD_REQUEST)

                user = User.objects.filter(email=email.lower()).last()

                if employee_id == '':
                    employee_id = None

                if sex == '':
                    sex = None
                else:
                    try:
                        sex = bool(int(sex))
                    except Exception:
                        return Response({"detail": ["性別のデータ形式が不正です"], 'code': status.HTTP_400_BAD_REQUEST, },
                                        status=status.HTTP_400_BAD_REQUEST)

                if email_magazine == 'N':
                    is_send_email = False
                else:
                    is_send_email = True

                if is_admin == 'Y':
                    group = self.admin_group
                else:
                    group = self.user_group


                if user is not None:
                    if workshop_code != '':
                        workshop = Workshop.objects.filter(code=workshop_code,company_id=company_id).first()

                        if workshop is not None and not UserWorkshop.objects.filter(user_id=user.id, workshop_id=workshop.id).exists():
                            UserWorkshop.objects.filter(user_id=user.id).delete()
                            UserWorkshop.objects.create(
                                user_id=user.id,
                                workshop_id=workshop.id,
                                company_id=company.id
                            )

                    user.first_name = first_name
                    user.last_name = last_name
                    user.save()

                    #update profile
                    profile = UserProfile.objects.filter(user=user).last()
                    if profile is None:
                        UserProfile.objects.create(
                            employee_id=employee_id,
                            user_id=user.id,
                            first_furigana=first_furigana,
                            last_furigana=last_furigana,
                            birthday=birthday,
                            sex=sex,
                            position_department=job_position,
                            department=department,
                            company_date_joined=date_joined,
                            company_id=company.id,
                            is_send_email=is_send_email,
                            lock_status='UNLOCKED',
                            no_login_attempt=0
                        )
                    else:
                        if int(company_id) == int(profile.company_id):
                            profile.first_furigana = first_furigana
                            profile.last_furigana = last_furigana
                            profile.birthday = birthday
                            profile.sex = sex
                            profile.position_department = job_position
                            profile.department = department
                            profile.company_date_joined = date_joined
                            profile.employee_id = employee_id
                            profile.is_send_email = is_send_email
                            profile.save()
                        else:
                            return Response({"detail": ["従業員はすでに別の会社に登録されています"], 'code': status.HTTP_400_BAD_REQUEST, },
                                            status=status.HTTP_400_BAD_REQUEST)
                    # remove and add group
                    user.groups.clear()
                    user.groups.add(group)

                else:
                    if employee_id is not None:
                        employee_id_exist = UserProfile.objects.filter(employee_id=employee_id,
                                                                       company_id=company_id).exists()
                        if employee_id_exist:
                            return Response({"detail": ["社員IDが既に登録されています"], 'employee_id': employee_id},
                                            status=status.HTTP_400_BAD_REQUEST)

                    user = User.objects.create(
                        first_name=first_name,
                        last_name=last_name,
                        username=email.lower(),
                        email=email.lower(),
                    )
                    password_string = randomStringDigits()
                    user.set_password(password_string)
                    user.save()
                    user.groups.add(group)

                    if workshop_code != '':
                        workshop = Workshop.objects.filter(code=workshop_code,company_id=company_id).first()
                        if workshop is not None:
                            if not UserWorkshop.objects.filter(user_id=user.id, workshop_id=workshop.id).exists():
                                UserWorkshop.objects.filter(user_id=user.id).delete()
                                UserWorkshop.objects.create(
                                    user_id=user.id,
                                    workshop_id=workshop.id,
                                    company_id=company.id
                                )

                    UserProfile.objects.create(
                        employee_id=employee_id,
                        user=user,
                        first_furigana=first_furigana,
                        last_furigana=last_furigana,
                        birthday=birthday,
                        sex=sex,
                        position_department=job_position,
                        department=department,
                        company_date_joined=date_joined,
                        company_id=company.id,
                        is_send_email=is_send_email,
                        lock_status='UNLOCKED',
                        no_login_attempt=0
                    )

                    password_string = create_token(user)
                    SendEmailWhenCreatedUser(user, email=user.email,password_string=password_string)
        except:
            return Response({"detail": ["予期せぬエラーが発生しました"], 'code': status.HTTP_500_INTERNAL_SERVER_ERROR, },
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        queryset = User.objects.all().order_by('-id')
        serializer = ListUserAdminSerializer(queryset, many=True)
        return Response({"data": serializer.data,'message':'登録が正常に完了しました', 'code': 200})


class ChangePasswordView(UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = ()

    def get_object(self, queryset=None):
        if "token" in self.request.data.keys():
            obj = ResetPasswordToken.objects.get(key=self.request.data['token']).user
        else:
            obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except ResetPasswordToken.DoesNotExist:
            return Response({"data": {
                'message': 'ユーザーが見つかりません'
            }, 'code': status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            response_errors = {
                'code': status.HTTP_400_BAD_REQUEST,
                'message': 'このパスワードは強力ではありません',
                'data': []
            }
            if re.search(r'[A-Za-z0-9@#$%^&+=]{8,}', serializer.data.get("password")) == None:
                return Response(response_errors, status=status.HTTP_400_BAD_REQUEST)

            response_errors = {
                'code': status.HTTP_400_BAD_REQUEST,
                'message': 'パスワードが一致しません',
                'data': []
            }
            if serializer.data.get("confirmed_password") != serializer.data.get("password"):
                return Response(response_errors, status=status.HTTP_400_BAD_REQUEST)

            self.object.set_password(serializer.data.get("password"))
            self.object.is_staff = True
            user = self.object.save()
            response = {
                'code': status.HTTP_200_OK,
                'message': 'パスワードの変更が完了しました。新しいパスワードでログインしてください',
                'data': []
            }
        if "token" in self.request.data.keys():
            ResetPasswordToken.objects.filter(key=self.request.data['token']).delete()
            return user_login(self.object,serializer.data.get("password"),request)
        return Response(response, status=status.HTTP_200_OK)


class SettingSendEmailUser(GenericAPIView):
    serializer_class = SettingSendEmailUserSerializer
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'POST': ['user','admin','coacha_admin'], 'GET': ['user','admin','coacha_admin']}

    def get(self, request, *args, **kwargs):
        user = request.user
        profile = UserProfile.objects.filter(user_id=user.id).first()
        data = SettingSendEmailUserSerializer(profile).data

        return Response({"data": data, 'code': 200}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = SettingSendEmailUserSerializer(data=request.data)
        user = request.user
        is_send_email = request.data['is_send_email']
        if serializer.is_valid():
            user_profile = user.userprofile
            user_profile.is_send_email = is_send_email
            user_profile.save()

            profile = UserProfile.objects.filter(user_id=user.id).first()
            data = SettingSendEmailUserSerializer(profile).data

            return Response({"data": data, 'code': 200}, status=status.HTTP_200_OK)


setting_send_email_user = SettingSendEmailUser.as_view()


class ForgotPasswordRequest(GenericAPIView):
    serializer_class = ForgotPasswordRequestSerializer
    throttle_classes = ()
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        serializer = ForgotPasswordRequestSerializer(data=request.data)
        try:
            user = User.objects.filter(email=request.data['email']).first()
            if user is None:
                return Response({"data": {
                    'message': 'ユーザーが見つかりません'
                }, 'code': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

            company = user.userprofile.company
            ip_check_result = True
            if company is not None:
                ip_check_result = IPCheck.check_ip(company.id, request)
            if ip_check_result is False:
                data = {
                    'data': {
                        'message': "ご利用の環境からのアクセスは管理者により制限されています"},
                        'code': status.HTTP_403_FORBIDDEN
                }
                return Response(data, status=status.HTTP_403_FORBIDDEN)

        except User.DoesNotExist:
            return Response({"data": {
                'message': 'ユーザーが見つかりません'
            }, 'code': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            r = requests.post(
                API_ENDPOINT + '/v1/django-forgot-password/',
                data={
                    'email': request.data['email'],
                },
            )

            if r.status_code == requests.codes.ok:
                return Response({"data": {
                    'message': 'ユーザーが見つかりません'
                }, 'code': 200}, status=status.HTTP_200_OK)

            # Return the error if it goes badly
            return Response(r.json(), r.status_code)


class AdminForgotPasswordRequest(GenericAPIView):
    serializer_class = ForgotPasswordRequestSerializer
    throttle_classes = ()
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        serializer = ForgotPasswordRequestSerializer(data=request.data)
        try:
            user = User.objects.filter(email=request.data['email'],groups__name__in=['admin','coacha_admin']).first()
            if user is None:
                return Response({"data": {
                    'message': 'ユーザーが見つかりません'
                }, 'code': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

            company = user.userprofile.company
            ip_check_result = True
            if company is not None:
                ip_check_result = IPCheck.check_ip(company.id, request)
            if ip_check_result is False:
                data = {
                    'data': {
                        'message': "ご利用の環境からのアクセスは管理者により制限されています"},
                    'code': status.HTTP_403_FORBIDDEN
                }
                return Response(data, status=status.HTTP_403_FORBIDDEN)

        except User.DoesNotExist:
            return Response({"data": {
                'message': 'ユーザーが見つかりません'
            }, 'code': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            r = requests.post(
                API_ENDPOINT + '/v1/django-forgot-password/',
                data={
                    'email': request.data['email'],
                },
            )

            if r.status_code == requests.codes.ok:
                return Response({"data": {
                    'message': 'ユーザーが見つかりません'
                }, 'code': 200}, status=status.HTTP_200_OK)

            # Return the error if it goes badly
            return Response(r.json(), r.status_code)


class ForgotPasswordConfirmRequest(GenericAPIView):
    serializer_class = ForgotPasswordConfirmSerializer
    throttle_classes = ()
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        serializer = ForgotPasswordConfirmSerializer(data=request.data)
        try:
            user = ResetPasswordToken.objects.get(key=request.data['token']).user
        except ResetPasswordToken.DoesNotExist:
            data = {
                'data': {'message': 'The key is not valid'},
                'code': status.HTTP_403_FORBIDDEN
            }
            return Response(data, status=status.HTTP_403_FORBIDDEN)
        # user = token.user
        if serializer.is_valid():
            r = requests.post(
                API_ENDPOINT + '/v1/django-forgot-password/confirm/',
                data={
                    'password': request.data['password'],
                    'token': request.data['token'],
                },
            )
            if r.status_code == requests.codes.ok:
                user_profile = user.userprofile
                user_profile.lock_status='UNLOCKED'
                user_profile.no_login_attempt=0
                user_profile.save()

                data = {
                    'message': 'OK',
                    'code': r.status_code
                }
                return Response(data, r.status_code)

            # Return the error if it goes badly
            return Response(r.json(), r.status_code)


class SendEmailToListUserJoinWorkshop(GenericAPIView):
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'POST': ['admin', 'coacha_admin']}

    def post(self, request, *args, **kwargs):
        try:
            list_users = request.data['list_users']
        except:
            return Response({"data": {
                'message': 'ユーザーリストは見つかりません'
            }, 'code': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

        for data in list_users:
            try:
                user = User.objects.get(pk=data['user_id'])
                full_name = user.first_name + user.last_name
                SendEmailRequestUserWorkshop(user, full_name,)
            except User.DoesNotExist:
                break

        return Response({"data": {'message': 'メール送信成功'}, 'code': 200})


class ActiveUser(GenericAPIView):
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'POST': ['admin', 'coacha_admin']}

    def post(self, request, *args, **kwargs):
        try:
            list_users = request.data['list_users']
        except:
            return Response({"data": {
                'message': 'ユーザーリストは見つかりません'
            }, 'code': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

        for user_id in list_users:
            try:
                user = User.objects.get(pk=user_id)
                user.is_active=True
                user.save()
                full_name = user.first_name + user.last_name
                SendEmailRequestUserWorkshop(user, full_name, )

            except User.DoesNotExist:
                break

        return Response({"data": {'message': 'メール送信成功'}, 'code': 200})


class DeActiveUser(GenericAPIView):
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'POST': ['admin', 'coacha_admin']}

    def post(self, request, *args, **kwargs):
        try:
            list_users = request.data['list_users']
        except:
            return Response({"data": {
                'message': 'ユーザーリストは見つかりません'
            }, 'code': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

        for user_id in list_users:
            try:
                user = User.objects.get(pk=user_id)
                user.is_active = False
                user.save()

            except User.DoesNotExist:
                break

        return Response({"data": {'message': 'メール送信成功'}, 'code': 200})


class RemoveListUser(GenericAPIView):
    serializer_class = ListUserAdminSerializer
    pagination_class = UserPagination
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'POST': ['admin', 'coacha_admin']}

    def post(self, request, *args, **kwargs):
        try:
            company_id = request.data['company_id']
        except:
            return Response({"data": {
                'message': '会社IDは見つかりません'
            }, 'code': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

        try:
            list_users = request.data['list_users']
        except:
            return Response({"data": {
                'message': 'ユーザーリストは見つかりません'
            }, 'code': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

        for user_id in list_users:
            try:
                user = User.objects.get(pk=user_id)
                if int(user.userprofile.company.id) == int(company_id):
                    user.delete()
            except User.DoesNotExist:
                break

        return Response({"data": {'message': 'メール送信成功'}, 'code': 200})


class CheckLogin(GenericAPIView):
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'GET': ['user', 'admin', 'coacha_admin']}

    def get(self, request, *args, **kwargs):
        company = request.user.userprofile.company
        if company is not None:
            ip_check_result = IPCheck.check_ip(company.id, request)
            if ip_check_result is False:
                data = {
                    'data': {
                        'message': "ご利用の環境からのアクセスは管理者により制限されています"},
                    'code': status.HTTP_403_FORBIDDEN
                }
                return Response(data, status=status.HTTP_403_FORBIDDEN)
        return Response({"data": {'message':'OK'}, 'code': 200},status=status.HTTP_200_OK)


class CheckAdminLogin(GenericAPIView):
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'GET': ['admin']}

    def get(self, request, *args, **kwargs):
        company = request.user.userprofile.company
        if company is not None:
            ip_check_result = IPCheck.check_ip(company.id, request)
            if ip_check_result is False:
                data = {
                    'data': {
                        'message': "ご利用の環境からのアクセスは管理者により制限されています"},
                    'code': status.HTTP_403_FORBIDDEN
                }
                return Response(data, status=status.HTTP_403_FORBIDDEN)
        return Response({"data": {'message': 'OK'}, 'code': 200}, status=status.HTTP_200_OK)


class CheckSupperAdminLogin(GenericAPIView):
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'GET': ['coacha_admin']}

    def get(self, request, *args, **kwargs):
        company = request.user.userprofile.company
        if company is not None:
            ip_check_result = IPCheck.check_ip(company.id, request)
            if ip_check_result is False:
                data = {
                    'data': {
                        'message': "ご利用の環境からのアクセスは管理者により制限されています"},
                    'code': status.HTTP_403_FORBIDDEN
                }
                return Response(data, status=status.HTTP_403_FORBIDDEN)
        return Response({"data": {'message': 'OK'}, 'code': 200}, status=status.HTTP_200_OK)


class CountUser(GenericAPIView):
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'GET': ['admin', 'coacha_admin']}

    def get(self, request, *args, **kwargs):
        try:
            company_id = request.GET['company_id']
        except:
            return Response({"data": {
                'message': '会社IDは見つかりません'
            }, 'code': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        q_objects = Q()
        q_objects &= Q(is_active=True)
        q_objects &= Q(userprofile__company_id=company_id)
        q_objects &= Q(groups__name__in=['admin', 'user'])
        total_user_active = User.objects.filter(q_objects).count()

        q_objects_total = Q()
        q_objects_total &= Q(userprofile__company_id=company_id)
        q_objects_total &= Q(groups__name__in=['admin', 'user'])

        total_user = User.objects.filter(q_objects_total).count()
        data = {
            'total_user_active': total_user_active,
            'total_user': total_user,
        }
        return Response({"data": data, 'code': 200}, status=status.HTTP_200_OK)


class UserDetail(GenericAPIView):
    serializer_class = ListUserAdminSerializer
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'GET': ['admin', 'coacha_admin']}

    def get_object(self):
        obj = User.objects.filter(pk=self.kwargs.get('pk')).first()
        return obj

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        data = self.get_serializer(user).data
        return Response(data, status=status.HTTP_200_OK)


class UserExport(GenericAPIView):
    # filter_backends = (SearchFilter, OrderingFilter)
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'GET': ['admin', 'coacha_admin']}

    def get(self, request, *args, **kwargs):
        user = request.user
        user_scope = str(user.groups.first())
        company_id = request.GET['company_id']
        if company_id is None:
            company_id = user.userprofile.company_id

        if user_scope == 'admin' and int(company_id) != user.userprofile.company_id:
            raise PermissionDenied('このCSVファイルをダウンロードする権限がありません');

        rows = []
        headers = CsvParser.HEADERS_DOWNLOAD
        rows.append([header["name"] for header in headers])
        userprofile_queryset = UserProfile.objects.filter(company_id=company_id)
        admin_group = Group.objects.get(name='admin')
        for user_entry in userprofile_queryset:
            values = []
            values.append('Y' if user_entry.user.is_active else 'N')
            values.append(user_entry.employee_id if user_entry.employee_id else '')
            values.append('Y' if admin_group in  user_entry.user.groups.all() else 'N')
            values.append(user_entry.user.last_name if user_entry.user.last_name else '')
            values.append(user_entry.user.first_name if user_entry.user.first_name else '')
            values.append(user_entry.last_furigana if user_entry.last_furigana else '')
            values.append(user_entry.first_furigana if user_entry.first_furigana else '')
            values.append(user_entry.user.email)
            user_workshop_entry = UserWorkshop.objects.filter(user=user_entry.user).last()
            values.append(user_workshop_entry.workshop.code if user_workshop_entry else '')
            values.append(user_workshop_entry.workshop.date_workshop.strftime('%Y/%m/%d') if user_workshop_entry else '')
            values.append('Y' if user_workshop_entry and user_workshop_entry.completed_assessment else 'N')
            values.append('Y' if user_entry.is_send_email else 'N')
            values.append(user_entry.user.last_login.strftime('%Y/%m/%d %H:%M:%S') if user_entry.user.last_login else '')
            values.append(user_entry.position_department)
            values.append(user_entry.department if user_entry.department else '')
            values.append(user_entry.company_date_joined.strftime('%Y/%m/%d') if user_entry.company_date_joined else '')
            values.append(user_entry.birthday.strftime('%Y/%m/%d') if user_entry.birthday else '')
            values.append('' if user_entry.sex is None else 1 if user_entry.sex else 0)
            rows.append(values)
        response = HttpResponse(content_type='text/csv')
        response.write(codecs.BOM_UTF8)
        writer = csv.writer(response)
        for row in rows:
            writer.writerow(row)
        return response


send_email_request_user = SendEmailToListUserJoinWorkshop.as_view()
remove_list_user = RemoveListUser.as_view()
forgot_password_request = ForgotPasswordRequest.as_view()
forgot_password_confirm_request = ForgotPasswordConfirmRequest.as_view()
check_login = CheckLogin.as_view()
check_admin_login = CheckAdminLogin.as_view()
check_supper_admin_login = CheckSupperAdminLogin.as_view()

# Admin forgot password
admin_forgot_password = AdminForgotPasswordRequest.as_view()
de_active_user = DeActiveUser.as_view()
active_user = ActiveUser.as_view()
count_user = CountUser.as_view()
detail_user = UserDetail.as_view()
