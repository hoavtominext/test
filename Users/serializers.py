import os
import datetime
import random
import string

from django.contrib.auth.password_validation import validate_password
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.encoding import force_text
from rest_framework import serializers, status
from rest_framework.exceptions import APIException

from Company.models import Company
from Department.models import Department
from Users.models import User, UserProfile
from Workshop.models import UserWorkshop, Workshop
from django.contrib.auth.models import Group
from django.core.validators import EmailValidator
from rest_framework.validators import UniqueTogetherValidator
from django_rest_passwordreset.models import ResetPasswordToken

WEB_CLIENT = os.getenv('WEB_CLIENT')


class ForgotPasswordRequestSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255, required=True)


class ForgotPasswordConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, required=True)
    token = serializers.CharField(max_length=255, required=True)


class SettingSendEmailUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=False)
    is_send_email = serializers.BooleanField(required=True)


class ListUserAdminSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField(max_length=100, required=True)
    username = serializers.CharField(max_length=100, required=True)
    is_superuser = serializers.BooleanField(required=False)
    is_active = serializers.BooleanField(required=False)
    is_staff = serializers.BooleanField(required=False)
    department = serializers.SerializerMethodField()
    employee_id = serializers.SerializerMethodField()
    first_furigana = serializers.SerializerMethodField()
    last_furigana = serializers.SerializerMethodField()
    is_send_email = serializers.SerializerMethodField()
    birthday = serializers.SerializerMethodField()
    sex = serializers.SerializerMethodField()
    position_department = serializers.SerializerMethodField()
    company_date_joined = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    date_workshop = serializers.SerializerMethodField()
    code_workshop = serializers.SerializerMethodField()
    workshop_id = serializers.SerializerMethodField()
    assessment = serializers.SerializerMethodField()
    send_mail_magazine = serializers.SerializerMethodField()
    last_login = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    def get_send_mail_magazine(self, user):
        try:
            user_profile =  UserProfile.objects.filter(user_id=user.id).first()
            return user_profile.is_send_email
        except:
            return False

    def get_assessment(self, user):
        try:
            user_workshop =  UserWorkshop.objects.filter(user_id=user.id).first()
            return user_workshop.completed_assessment
        except:
            return False

    def get_code_workshop(self, user):
        try:
            workshop =  Workshop.objects.filter(userworkshop__user_id=user.id).first()
            return workshop.code
        except:
            return ''
    def get_workshop_id(self, user):
        try:
            workshop =  Workshop.objects.filter(userworkshop__user_id=user.id).first()
            return workshop.id
        except:
            return ''

    def get_date_workshop(self, user):
        try:
            workshop =  Workshop.objects.filter(userworkshop__user_id=user.id).first()
            return workshop.date_workshop
        except:
            return ''

    def get_is_admin(self, obj):
        if obj.groups.filter(name='admin').exists():
            return True
        else:
            return False

    def get_full_name(self, obj):
        try:
            full_name = obj.last_name + ' ' + obj.first_name
            return full_name

        except Workshop.DoesNotExist:
            return ''

    def get_company(self, obj):
        try:
            if obj.userprofile.company_id:
                company = Company.objects.filter(pk=obj.userprofile.company_id).first()
                return company.name
        except UserProfile.DoesNotExist:
            return ''

    def get_company_date_joined(self, obj):
        try:
            if obj.userprofile.company_date_joined:
                return obj.userprofile.company_date_joined
        except UserProfile.DoesNotExist:
            return ''

    def get_position_department(self, obj):
        try:
            if obj.userprofile.position_department:
                return obj.userprofile.position_department
        except UserProfile.DoesNotExist:
            return ''

    def get_sex(self, obj):
        try:
            if obj.userprofile:
                return obj.userprofile.sex
        except UserProfile.DoesNotExist:
            return None

    def get_birthday(self, obj):
        try:
            if obj.userprofile.birthday:
                return obj.userprofile.birthday
        except UserProfile.DoesNotExist:
            return ''

    def get_is_send_email(self, obj):
        try:
            if obj.userprofile.is_send_email:
                return obj.userprofile.is_send_email
        except UserProfile.DoesNotExist:
            return False

    def get_department(self, obj):
        try:
            if obj.userprofile.department:
                return obj.userprofile.department
        except UserProfile.DoesNotExist:
            return ''

    def get_employee_id(self, obj):
        try:
            if obj.userprofile.employee_id:
                return obj.userprofile.employee_id
        except UserProfile.DoesNotExist:
            return None

    def get_first_furigana(self, obj):
        try:
            if obj.userprofile.first_furigana:
                return obj.userprofile.first_furigana
        except UserProfile.DoesNotExist:
            return ''

    def get_last_furigana(self, obj):
        try:
            if obj.userprofile.last_furigana:
                return obj.userprofile.last_furigana
        except UserProfile.DoesNotExist:
            return ''


def randomStringDigits(stringLength=8):
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))

class CustomValidation(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'A server error occurred.'

    def __init__(self, detail, field, status_code):
        if status_code is not None:self.status_code = status_code
        if detail is not None:
            self.detail = {'detail': force_text(detail)}
        else: self.detail = {'detail': force_text(self.default_detail)}

# normal serializer [similar to forms.Form]
class UserSerializer(serializers.Serializer):
    is_user_admin = serializers.BooleanField(required=True)
    employee_id = serializers.CharField(required=False,allow_null=True)
    first_name = serializers.CharField(max_length=100, required=True)
    last_name = serializers.CharField(max_length=100, required=True)
    first_furigana = serializers.CharField(max_length=100, required=True,allow_blank=True,allow_null=True)
    last_furigana = serializers.CharField(max_length=100, required=True,allow_blank=True,allow_null=True)
    email = serializers.EmailField(max_length=100, required=True)
    username = serializers.EmailField(max_length=100, required=True)
    is_send_email = serializers.BooleanField(required=True)
    birthday = serializers.CharField(required=False,allow_blank=True,allow_null=True)
    sex = serializers.BooleanField(required=False,allow_null=True)
    department = serializers.CharField(required=False,allow_blank=True, allow_null=True)
    position_department = serializers.CharField(required=False,allow_blank=True,allow_null=True)
    company_date_joined = serializers.CharField(required=False,allow_blank=True,allow_null=True)
    workshop_id = serializers.CharField(required=False,allow_blank=True,allow_null=True)
    company_id = serializers.IntegerField(required=True)

    def validate(self, data):
        try:
            employee_id = data['employee_id']
        except:
            employee_id = None

        try:
            company_id = data['company_id']
        except:
            raise CustomValidation("会社は存在しません", 'company_id', status_code=status.HTTP_400_BAD_REQUEST)

        if employee_id is not None and employee_id != '':
            if self.instance is None:
                employee_id_exits = (UserProfile.objects.filter(employee_id=employee_id,company_id=company_id)).exists()
                if employee_id_exits:
                    raise CustomValidation("社員IDが既に登録されています", 'employee_id', status_code=status.HTTP_400_BAD_REQUEST)
            else:
                #update
                self_employee_id = self.instance.userprofile.employee_id
                if self_employee_id != employee_id:
                    employee_id_exits = UserProfile.objects.filter(Q(employee_id=employee_id,company_id=company_id)).exists()
                    if employee_id_exits is True:
                        raise CustomValidation("社員IDが既に登録されています", 'employee_id', status_code=status.HTTP_400_BAD_REQUEST)

        return data

    def validate_username(self, username):
        if self.instance is None:
            username_exits = (User.objects.filter(username=username)).exists()
            if username_exits:
                raise CustomValidation("メールアドレスが既に登録されています",'email',status_code=status.HTTP_400_BAD_REQUEST)
        else:
            #update
            self_username = self.instance.username
            if self_username != username:
                username_exits = User.objects.filter(Q(email=username)).exists()
                if username_exits is True:
                    raise CustomValidation("メールアドレスが既に登録されています",'email',status_code=status.HTTP_400_BAD_REQUEST)

        return username

    def validate_email(self, email):
        if self.instance is None:
            email_exits = (User.objects.filter(email=email)).exists()
            if email_exits:
                raise CustomValidation("メールアドレスが既に登録されています",'email',status_code=status.HTTP_400_BAD_REQUEST)
        else:
            #update
            self_email = self.instance.email
            if self_email != email:
                email_exits = User.objects.filter(Q(email=email)).exists()
                if email_exits is True:
                    raise CustomValidation("メールアドレスが既に登録されています",'email',status_code=status.HTTP_400_BAD_REQUEST)

        return email

    def validate_company_id(self, company_id):
        if not Company.objects.filter(pk=company_id).exists():
            raise CustomValidation("会社は存在しません", 'company_id', status_code=status.HTTP_400_BAD_REQUEST)
        return company_id

    def validate_birthday(self, birthday):
        if birthday != '':
            try:
                d = datetime.datetime.strptime(birthday, '%Y-%m-%d')
                birthday = d.strftime('%Y-%m-%d')
            except ValueError:
                try:
                    d = datetime.datetime.strptime(birthday, '%Y/%m/%d')
                    birthday = d.strftime('%Y-%m-%d')
                except:
                    raise CustomValidation("存在しない日付です", 'company_id', status_code=status.HTTP_400_BAD_REQUEST)
        return birthday

    # is called if we save serializer if it do not have an instance
    def create(self, validated_data):
        user_data = {
            'first_name': validated_data['first_name'],
            'last_name': validated_data['last_name'],
            'email':validated_data['email'],
            'username':validated_data['username'],
        }
        user = User.objects.create(**user_data)
        password_string = create_token(user)
        # user.set_password(password_string)
        user.is_staff = False
        user.save()

        is_user_admin = validated_data['is_user_admin']
        if is_user_admin is True:
            group = Group.objects.filter(name='admin').first()
        else:
            group = Group.objects.filter(name='user').first()

        user.groups.add(group)

        try:
            profile = UserProfile.objects.filter(user_id=user.id).first()
        except UserProfile.DoesNotExist:
            profile = None

        if profile is None:
            try:
                sex = validated_data['sex']
                if sex == '':
                    sex = None
            except:
                sex = None

            try:
                employee_id = validated_data['employee_id']
                if employee_id == '':
                    employee_id = None
            except:
                employee_id = None

            try:
                birthday = validated_data['birthday']
                datetime.datetime.strptime(birthday, '%Y-%m-%d')
            except:
                birthday = None

            try:
                position_department = validated_data['position_department']
            except:
                position_department = None

            try:
                company_date_joined = validated_data['company_date_joined']
                datetime.datetime.strptime(company_date_joined, '%Y-%m-%d')
            except:
                company_date_joined = None

            try:
                is_send_email = validated_data['is_send_email']
            except:
                is_send_email = False

            try:
                department = validated_data['department']
            except:
                department = None

            profile = UserProfile.objects.create(
                employee_id=employee_id,
                first_furigana=validated_data['first_furigana'],
                last_furigana=validated_data['last_furigana'],
                birthday=birthday,
                sex=sex,
                position_department=position_department,
                company_date_joined=company_date_joined,
                is_send_email=is_send_email,
                company_id=int(validated_data['company_id']),
                department=department,
                user_id=user.id
            )
            profile.save()

        workshop_id = validated_data['workshop_id']
        if workshop_id is not '':
            if not UserWorkshop.objects.filter(user_id=user.id, workshop_id=workshop_id).exists():
                UserWorkshop.objects.filter(user_id=user.id).delete()
                UserWorkshop.objects.create(
                    user_id=user.id,
                    workshop_id=workshop_id
                )
        SendEmailWhenCreatedUser(user, email=user.email,password_string=password_string)
        return user

    # is called if we save serializer if it have an instance
    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        instance.is_staff = validated_data.get('is_staff', instance.is_staff)
        instance.save()

        is_user_admin = validated_data.get('is_user_admin', False)
        if is_user_admin is True:
            group = Group.objects.filter(name='admin').first()
        else:
            group = Group.objects.filter(name='user').first()

        #remove and add group
        instance.groups.remove(group)
        instance.groups.clear()
        instance.groups.add(group)
        profile = UserProfile.objects.filter(user_id=instance.id).first()

        try:
            birthday = validated_data.get('birthday', profile.birthday)
            datetime.datetime.strptime(birthday, '%Y-%m-%d')
        except:
            birthday = None

        try:
            company_date_joined = validated_data.get('company_date_joined', profile.company_date_joined)
            datetime.datetime.strptime(company_date_joined, '%Y-%m-%d')
        except:
            company_date_joined = None

        try:
            employee_id = validated_data.get('employee_id')
            if employee_id == '':
                employee_id = None
        except:
            employee_id = None

        try:
            sex = validated_data.get('sex')
            if sex == '':
                sex = None
        except:
            sex = None

        profile.employee_id = employee_id
        profile.first_furigana = validated_data.get('first_furigana', profile.first_furigana)
        profile.last_furigana = validated_data.get('last_furigana', profile.last_furigana)
        profile.birthday = birthday
        profile.sex = sex
        profile.position_department = validated_data.get('position_department', profile.position_department)
        profile.company_date_joined = company_date_joined
        profile.is_send_email = validated_data.get('is_send_email', profile.is_send_email)
        profile.company_id = validated_data.get('company_id', profile.company_id)
        profile.department = validated_data.get('department', profile.department)
        profile.user_id = validated_data.get('user_id', profile.user_id)
        profile.save()

        workshop_id = validated_data['workshop_id']
        if workshop_id:
            if not UserWorkshop.objects.filter(user_id=instance.id, workshop_id=workshop_id).exists():
                UserWorkshop.objects.filter(user_id=instance.id).delete()
                UserWorkshop.objects.create(
                    user_id=instance.id,
                    workshop_id=workshop_id
            )
        return instance

# normal serializer [similar to forms.Form]
class UserUpdateSerializer(serializers.Serializer):
    model = User

    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField(max_length=100, required=False)
    username = serializers.CharField(max_length=100, required=False)
    is_superuser = serializers.BooleanField()
    is_staff = serializers.BooleanField()

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.save()
        return user

    # is called if we save serializer if it have an instance
    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        instance.is_staff = validated_data.get('is_staff', instance.is_staff)
        instance.save()

        return instance


class ChangePasswordSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    password = serializers.CharField(required=True)
    confirmed_password = serializers.CharField(required=True, max_length=30)


# normal serializer [similar to forms.Form]
class ImportUserSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False)
    email = serializers.EmailField(max_length=100, required=True)
    hurigana = serializers.CharField(max_length=100, required=False)
    furigana = serializers.CharField(max_length=100, required=False)
    language = serializers.CharField(max_length=10, required=False)
    birthday = serializers.DateTimeField(required=False)
    sex = serializers.CharField(required=False)
    position = serializers.CharField(required=False)
    date_joined = serializers.DateField(required=False)
    authority = serializers.CharField(required=False)

    # is called if we save serializer if it do not have an instance
    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password('123456aA@')
        user.save()
        return user

    # is called if we save serializer if it have an instance
    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        instance.is_staff = validated_data.get('is_staff', instance.is_staff)
        instance.save()

        return instance

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "username", "is_superuser")
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=['username', 'email']
            )
        ]


class UserLogoutSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=100, required=True)


class UserRefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=100, required=True)


def SendEmailWhenCreatedUser(user, email, password_string):
    # send an e-mail to the user
    context = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'password_string': WEB_CLIENT+"/change-password-first-time?token="+password_string,
    }

    # render email text
    email_html_message = render_to_string('first-time-login/password_setting_mail.html', context)
    msg = EmailMultiAlternatives(
        # title:
        ("【3分間コーチ】事前アセスメント実施のご案内".format(title="today")),
        # message:
        email_html_message,
        # from:
        "coacha_3mins@coacha.com",
        # to:
        [email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()


def SendEmailRequestUserWorkshop(user, admin_name):
    password_string = create_token(user)
    context = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'password_string': WEB_CLIENT+"/change-password-first-time?token="+password_string,
    }

    # render email text
    email_html_message = render_to_string('first-time-login/password_setting_mail.html', context)
    msg = EmailMultiAlternatives(
        # title:
        ("【3分間コーチ】事前アセスメント実施のご案内".format(title="today")),
        # message:
        email_html_message,
        # from:
        "coacha_3mins@coacha.com",
        # to:
        [user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()

def create_token(user):
    password_string = randomStringDigits(26)
    ResetPasswordToken.objects.create(
        user=user,
        user_agent='',
        ip_address='127.0.0.1',
        key=password_string
    )
    return  password_string