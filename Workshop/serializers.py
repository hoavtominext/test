from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from django.db.models import Q
from Workshop import models
from .models import Workshop
from rest_framework.response import Response

from rest_framework.validators import UniqueTogetherValidator
from random import choice, random
import string
from rest_framework import serializers, exceptions, status
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from Users.models import User
from rest_framework.exceptions import APIException
from django.utils.encoding import force_text
CODE_WORKSHOP = 'WS'

class ListWorkshopSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    code = serializers.CharField(required=False)
    name = serializers.CharField(max_length=100,required=False)
    date_workshop = serializers.DateField(required=True)
    remark = serializers.CharField(required=False, allow_blank=True)
    total_user_join = serializers.IntegerField(required=False)
    company_id = serializers.IntegerField(required=True)
    total_user_active = serializers.SerializerMethodField()
    total_user = serializers.SerializerMethodField()
    user_complete_assessment = serializers.SerializerMethodField()
    user_active_complete_assessment = serializers.SerializerMethodField()

    def get_total_user_active(self, workshop):

        company_id = workshop.company.id
        q_objects = Q()
        q_objects &= Q(is_active=True)
        q_objects &= Q(userprofile__company_id=company_id)
        q_objects &= Q(userworkshop__workshop_id=workshop.id)
        q_objects &= Q(groups__name__in=['admin', 'user'])

        total_active = User.objects.filter(q_objects).count()
        return total_active

    def get_total_user(self, workshop):
        company_id = workshop.company.id
        q_objects = Q()
        q_objects &= Q(userprofile__company_id=company_id)
        q_objects &= Q(userworkshop__workshop_id=workshop.id)
        q_objects &= Q(groups__name__in=['admin', 'user'])

        total_active = User.objects.filter(q_objects).count()
        return total_active

    def get_user_active_complete_assessment(self, workshop):
        company_id = workshop.company.id
        q_objects = Q()
        q_objects &= Q(is_active=True)
        q_objects &= Q(userprofile__company_id=company_id)
        q_objects &= Q(userworkshop__completed_assessment=True)
        q_objects &= Q(userworkshop__workshop_id=workshop.id)
        q_objects &= Q(groups__name__in=['admin', 'user'])

        user_complete_assessment = User.objects.filter(q_objects).count()
        return user_complete_assessment

    def get_user_complete_assessment(self, workshop):
        company_id = workshop.company.id
        q_objects = Q()
        q_objects &= Q(is_active=True)
        q_objects &= Q(userprofile__company_id=company_id)
        q_objects &= Q(userworkshop__workshop_id=workshop.id)
        q_objects &= Q(groups__name__in=['admin', 'user'])

        user_complete_assessment = User.objects.filter(q_objects).count()
        return user_complete_assessment
    class Meta:
        model = Workshop
        fields = ('id', 'code', 'name','date_workshop','total_user_join','remark',
                  'total_user_active','total_user','user_complete_assessment','user_active_complete_assessment','company_id')

class CustomValidation(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'A server error occurred.'

    def __init__(self, detail, field, status_code):
        if status_code is not None:self.status_code = status_code
        if detail is not None:
            self.detail = {'detail': force_text(detail)}
        else: self.detail = {'detail': force_text(self.default_detail)}

class WorkshopSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100,required=False, allow_blank=True)
    date_workshop = serializers.DateField(required=True)
    remark = serializers.CharField(required=False, allow_blank=True)
    total_user_join = serializers.IntegerField(required=False)
    company_id = serializers.IntegerField(required=True)

    def validate(self, data):
        if self.instance is None:
            date_workshop_exits = (Workshop.objects.filter(date_workshop=data['date_workshop'],company_id=data['company_id'])).exists()
            if date_workshop_exits:
                raise CustomValidation("ワークショップの日が作成されました", 'date_workshop', status_code=status.HTTP_400_BAD_REQUEST)
        else:
            #update
            self_date_workshop = self.instance.date_workshop
            if self_date_workshop != data['date_workshop']:
                date_workshop_exits = (Workshop.objects.filter(date_workshop=data['date_workshop'])).exists()
                if date_workshop_exits is not None:
                    raise CustomValidation("ワークショップの日が作成されました", 'date_workshop',
                                           status_code=status.HTTP_400_BAD_REQUEST)

        return data

    # is called if we save serializer if it do not have an instance
    def create(self, validated_data):
        company_id = validated_data.get('company_id')
        workshop_last = Workshop.objects.filter(company_id=company_id).last()
        if workshop_last is None:
            code = '001'
        else:
            workshop_code = workshop_last.code[2:]
            code = int(workshop_code)
            code = code + 1

        workshop = Workshop.objects.create(**validated_data)
        workshop.code = CODE_WORKSHOP + str(code).zfill(3)
        workshop.save()

        return workshop

    # is called if we save serializer if it have an instance
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.date_workshop = validated_data.get('date_workshop', instance.date_workshop)
        instance.remark = validated_data.get('remark', instance.remark)
        instance.save()

        return instance

    class Meta:
        model = models.Workshop
        fields = ('id', 'name', 'date_workshop','remark', 'total_user_join', 'company_id')

class ManyWorkshopSerializer(serializers.Serializer):
    workshops = serializers.JSONField(required=True)
    company_id = serializers.IntegerField(required=True)

    def create(self, validated_data):
        try:
            with transaction.atomic():
                results = validated_data['workshops']
                # save table answer
                for data in results:
                    code = CODE_WORKSHOP + str(int(Workshop.objects.last().id) + 1)
                    name = data['name']
                    date_workshop = data['date_workshop']
                    company_id = data['company_id']

                    if Workshop.objects.filter(date_workshop=date_workshop, company_id=company_id).exists():
                        # raise serializers.ValidationError(_('登録ワークショップ, %(value)s'), params={'value': date_workshop},)
                        errors = {}
                        errors['date_workshop'] = _('登録ワークショップ, ' + date_workshop)
                        raise ValidationError(errors)

                    workshop = Workshop.objects.create(
                        name=name,
                        code=code,
                        date_workshop=date_workshop,
                        company_id=company_id
                    )
                    workshop.save()

            return True

        except IndentationError:
            transaction.set_rollback(True)
            raise exceptions.ValidationError({
                '500': [(
                    "500 Errors")],
            })

    # is called if we save serializer if it have an instance
    def update(self, instance, validated_data):
        return instance