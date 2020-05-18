from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.db.models import Count
from django.template.loader import render_to_string
from oauth2_provider.contrib.rest_framework import TokenHasScope, OAuth2Authentication
from rest_framework.generics import get_object_or_404, GenericAPIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status, exceptions
from rest_framework.exceptions import PermissionDenied
from EmailPostLearningContent.models import EmailPostContent
from Question.serializers import getLastWorkshopJoin
from Users.models import User
from Workshop.models import Workshop
from Answer.models import Result, numberPeopleCompleted, numberPeopleCompletedThisMonth, \
    numberPeopleCompletedSecondMonth, numberPeopleCompletedThreeMonth, numberPeoplePreAssessment, countWorkshopCompany
from Workshop.serializers import WorkshopSerializer
from Users.serializers import UserSerializer, UserLogoutSerializer, UserRefreshTokenSerializer
from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created

import requests
from rest_framework.views import APIView
import os
from django.utils.crypto import get_random_string
from Company.models import CompanyIpList
from .serializers import CreateUserSerializer
from django.contrib.auth.models import update_last_login

API_ENDPOINT = os.getenv('API_ENDPOINT')
WEB_CLIENT = os.getenv('WEB_CLIENT')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')


class TokenHasScopeForMethod(TokenHasScope):

    def has_permission(self, request, view):
        token = request.auth

        if not token:
            return False

        if hasattr(token, "scope"):
            required_scopes = view.required_scopes_per_method[request.method]
            if token.scope in required_scopes:
                required_scopes = [token.scope]
            return token.is_valid(required_scopes)

class LoginAdmin(GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        username = request.data['username'].lower()
        # email = request.data['email']
        if username is None:
            data = {
                'data': {'message': 'メールアドレスが見つかりません'},
                'code': status.HTTP_403_FORBIDDEN
            }
            return Response(data, status=status.HTTP_403_FORBIDDEN)
        try:
            user = User.objects.get(username=username)
            scope = str(user.groups.first())
            if scope == 'None':
                scope = 'user'
            if scope not in ['admin', 'coacha_admin']:
                data = {
                    'data': {'message': 'メールアドレスまたはパスワードが違います'},
                    'code': status.HTTP_403_FORBIDDEN
                }
                return Response(data, status=status.HTTP_403_FORBIDDEN)

            if user.userprofile.lock_status !='UNLOCKED':
                data = {
                    'data': {'message': 'メールアドレスまたはパスワードが違います'},
                    'code': status.HTTP_403_FORBIDDEN
                }
                return Response(data, status=status.HTTP_403_FORBIDDEN)

            if not user.check_password(request.data['password']):
                data = {
                    'data': {'message': 'メールアドレスまたはパスワードが違います'},
                    'code': status.HTTP_400_BAD_REQUEST
                }
                if user is not None and user.userprofile.no_login_attempt < 5 and user.userprofile.lock_status == 'UNLOCKED':
                    user_profile = user.userprofile
                    user_profile.no_login_attempt += 1
                    user_profile.save()
                elif user is not None and user.userprofile.no_login_attempt == 5 and user.userprofile.lock_status == 'UNLOCKED':
                    user.userprofile.lock_status = "LOCKED"
                    user.userprofile.save()
                    send_password_reset(user=user)
                    data = {
                        'data': {"message": "メールアドレスまたはパスワードが違います","code": "locked"},
                        'code': status.HTTP_403_FORBIDDEN
                    }
                    return Response(data, status=status.HTTP_403_FORBIDDEN)
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            data = {
                'data': {'message': 'メールアドレスまたはパスワードが違います'},
                'code': status.HTTP_403_FORBIDDEN
            }
            return Response(data, status=status.HTTP_403_FORBIDDEN)

        data = {
            'grant_type': 'password',
            'username': username,
            'password': request.data['password'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'scope': scope,
        }
        r = requests.post(API_ENDPOINT + '/o/token/', data=data)

        try:
            company = user.userprofile.company
            ip_check_result = IPCheck.check_ip(company.id, request)
            if ip_check_result is False:
                data = {
                    'data': {'message': "ご利用の環境からのアクセスは管理者により制限されています"},
                    'code': status.HTTP_403_FORBIDDEN
                }
                return Response(data, status=status.HTTP_403_FORBIDDEN)

        except ObjectDoesNotExist:
            raise exceptions.ValidationError({
                'company': [(
                    "User company is not Exits")],
            })

        data_response = r.json()
        count_send_email = 0
        count_email_monthly = EmailPostContent.objects.filter(user_id=user.id).first()
        if count_email_monthly is not None:
            count_send_email = count_email_monthly.count_send_email

        is_supper_admin = False
        if user.groups.filter(name__in=['coacha_admin']).count() > 0:
            is_supper_admin = True

        data_response.update({
            'user_id': user.id,
            'email': user.email,
            'user_first_name': user.first_name,
            'user_last_name': user.last_name,
            'is_staff': user.is_staff,
            'company_id': company.id,
            'company_name': company.name,
            'count_company_workshop': countWorkshopCompany(company.id),
            'number_people_pre_assessment': numberPeoplePreAssessment(company.id),
            'number_people_completed': numberPeopleCompleted(company.id),
            'count_send_email': count_send_email,
            'is_supper_admin': is_supper_admin,
        })
        user_profile = user.userprofile
        user_profile.no_login_attempt = 0
        user_profile.save()
        update_last_login(None, user)
        return Response({"data": data_response, 'code': r.status_code}, status=r.status_code)


login_admin = LoginAdmin.as_view()


class Login(GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        username = request.data['username'].lower()
        # email = request.data['email']
        if username is None:
            data = {
                'data': {'message': 'メールアドレスまたはパスワードが違います'},
                'code': status.HTTP_403_FORBIDDEN
            }
            return Response(data, status=status.HTTP_403_FORBIDDEN)

        try:
            user = User.objects.get(username=username)
            if user.userprofile.lock_status !='UNLOCKED':
                data = {
                    'data': {'message': 'メールアドレスまたはパスワードが違います'},
                    'code': status.HTTP_403_FORBIDDEN
                }
                return Response(data, status=status.HTTP_403_FORBIDDEN)

            if not user.check_password(request.data['password']):
                data = {
                    'data': {'message': 'メールアドレスまたはパスワードが違います'},
                    'code': status.HTTP_400_BAD_REQUEST
                }
                if user is not None and user.userprofile.no_login_attempt < 5 and user.userprofile.lock_status == 'UNLOCKED':
                    user_profile = user.userprofile
                    user_profile.no_login_attempt += 1
                    user_profile.save()
                elif user is not None and user.userprofile.no_login_attempt == 5 and user.userprofile.lock_status == 'UNLOCKED':
                    user.userprofile.lock_status = "LOCKED"
                    user.userprofile.save()
                    send_password_reset(user=user)
                    data = {
                        'data': {"message": "メールアドレスまたはパスワードが違います","code": "locked"},
                        'code': status.HTTP_403_FORBIDDEN
                    }
                    return Response(data, status=status.HTTP_403_FORBIDDEN)
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            data = {
                'data': {'message': 'メールアドレスまたはパスワードが違います'},
                'code': status.HTTP_403_FORBIDDEN
            }
            return Response(data, status=status.HTTP_403_FORBIDDEN)
        return user_login(user,request.data['password'], request)

login = Login.as_view()


class Logout(GenericAPIView):
    serializer_class = UserLogoutSerializer
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        r = requests.post(
            API_ENDPOINT + '/o/revoke-token/',
            data={
                'token': request.data['token'],
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
            },
        )
        # If it goes well return sucess message (would be empty otherwise)
        if r.status_code == requests.codes.ok:
            data = {
                'data': {
                    'message': 'Logout success',
                    'code': r.status_code
                }
            }
            return Response(data, r.status_code)
        # Return the error if it goes badly
        return Response(r.json(), r.status_code)


logout = Logout.as_view()


class RefreshToken(GenericAPIView):
    serializer_class = UserRefreshTokenSerializer
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        r = requests.post(
            API_ENDPOINT + '/o/token/',
            data={
                'grant_type': 'refresh_token',
                'refresh_token': request.data['refresh_token'],
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
            },
        )
        return Response({"data": r.json(), 'code': r.status_code}, status=r.status_code)


refresh_token = RefreshToken.as_view()


@api_view(['POST'])
@permission_classes([AllowAny])
@receiver(reset_password_token_created)
def password_reset_token_created(sender, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender:
    :param reset_password_token:
    :param args:
    :param kwargs:
    :return:
    """
    # send an e-mail to the user

    is_supper_user = str(reset_password_token.user.groups.first())
    if is_supper_user =='coacha_admin' or is_supper_user=='admin':
        url_web_link = WEB_CLIENT + "/admin/forgot-password-confirm?token={token}".format(token=reset_password_token.key)
    else:
        url_web_link = WEB_CLIENT + "/forgot-password-confirm?token={token}".format(token=reset_password_token.key)
    user_profile = reset_password_token.user.userprofile
    context = {
        'current_user': reset_password_token.user,
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        'full_name': reset_password_token.user.last_name + reset_password_token.user.first_name,
        # ToDo: The URL can (and should) be constructed using pythons built-in `reverse` method.
        'reset_password_url': url_web_link
    }
    if user_profile.lock_status == "LOCKED":
        email_html_message = render_to_string('email/user_account_lock.html', context)
        msg = EmailMultiAlternatives(
        # title:
        ("【3分間コーチ】アカウントがロックされました"),
        # message:
        email_html_message,
        # from:
        "coacha_3mins@coacha.com",
        # to:
        [reset_password_token.user.email]
    )
    else:
        # render email text
        email_html_message = render_to_string('email/user_reset_password.html', context)
        # email_plaintext_message = render_to_string('email/user_reset_password.txt', context)

        msg = EmailMultiAlternatives(
            # title:
            ("【3分間コーチ】パスワード再設定のご案内"),
            # message:
            email_html_message,
            # from:
            "coacha_3mins@coacha.com",
            # to:
            [reset_password_token.user.email]
        )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()


def send_password_reset(user):
        user.password = get_random_string()
        user.save()
        r = requests.post(
            API_ENDPOINT + '/v1/django-forgot-password/',
            data={
                'email': user.email,
            },
        )


class IPCheck(APIView):
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'POST': ['coacha_admin', 'admin', 'user']}

    @staticmethod
    def check_ip(company_id, request):
        if company_id:
            company_ip_list = CompanyIpList.objects.filter(company_id=company_id).values_list('ip_address', flat=True)
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
            if len(company_ip_list) != 0 and not ip in company_ip_list:
                return False
        return True

    def post(self, request, *args, **kwargs):
        if not IPCheck.check_ip(request.user.company_id,request):
            raise PermissionDenied('ご利用の環境からのアクセスは管理者により制限されています')
        return Response({"OK"},status=status.HTTP_200_OK)

def user_login(user,password, request):

        scope = str(user.groups.first())
        if scope == 'None':
            scope = 'user'
        data = {
            'grant_type': 'password',
            'username': user.username,
            'password': password,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'scope': scope,
        }
        company = user.userprofile.company
        ip_check_result = IPCheck.check_ip(company.id, request)
        if ip_check_result is False :
            data = {
                'data': {'message': "ご利用の環境からのアクセスは管理者により制限されています"},
                'code': status.HTTP_403_FORBIDDEN
            }
            return Response(data, status=status.HTTP_403_FORBIDDEN)

        workshop_id = getLastWorkshopJoin(company_id=company.id)
        try:
            result = Result.objects.filter(company_id=company.id, user_id=user.id, workshop_id=workshop_id).order_by(
                '-count_assessment').first()
            if result is None:
                count_assessment = 0
            else:
                count_assessment = result.count_assessment
        except Result.DoesNotExist:
            count_assessment = 0

        r = requests.post(API_ENDPOINT + '/o/token/', data=data)
        data_response = r.json()
        data_response.update({
            'user_id': user.id,
            'is_staff': user.is_staff,
            'email': user.email,
            'user_first_name': user.first_name,
            'user_last_name': user.last_name,
            'count_assessment': count_assessment,
        })
        user_profile = user.userprofile
        user_profile.no_login_attempt =0
        user_profile.save()
        update_last_login(None, user)
        return Response({"data": data_response, 'code': r.status_code}, status=r.status_code)
