from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Company, CompanyIpList


# normal serializer [similar to forms.Form]
class CompanySerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True)
    date_contract_start = serializers.DateTimeField(required=True,format='%Y-%m-%d')
    date_contract_end = serializers.DateTimeField(required=True,format='%Y-%m-%d')
    remark = serializers.CharField(required=False,allow_blank=True)
    created_at = serializers.DateTimeField(required=False,format='%Y-%m-%d')
    updated_at = serializers.DateTimeField(required=False,format='%Y-%m-%d')


class CompanyCreateSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    date_contract_start = serializers.CharField(required=True)
    date_contract_end = serializers.CharField(required=True)
    created_at = serializers.DateTimeField(required=False)
    updated_at = serializers.DateTimeField(required=False)
    remark = serializers.CharField(required=False,allow_blank=True)

    def validate(self, data):
        if data['date_contract_start'] > data['date_contract_end']:
            raise serializers.ValidationError("契約の終了日は契約の開始日より小さくありません")
        return data

    # is called if we save serializer if it do not have an instance
    def create(self, validated_data):
        company = Company.objects.create(**validated_data)
        company.save()
        return company

    # is called if we save serializer if it have an instance
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.date_contract_start = validated_data.get('date_contract_start', instance.date_contract_start)
        instance.date_contract_end = validated_data.get('date_contract_end', instance.date_contract_end)
        instance.save()

        return instance


class CompanyEditSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    date_contract_start = serializers.DateField(required=True)
    date_contract_end = serializers.DateField(required=True)
    created_at = serializers.DateTimeField(required=False)
    updated_at = serializers.DateTimeField(required=False)
    remark = serializers.CharField(required=False,allow_blank=True)
    def validate(self, data):
        if data['date_contract_start'] > data['date_contract_end']:
            raise serializers.ValidationError("契約の終了日は契約の開始日より小さくありません")
        return data

    # is called if we save serializer if it do not have an instance
    def create(self, validated_data):
        company = Company.objects.create(**validated_data)
        company.save()
        return company

    # is called if we save serializer if it have an instance
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.date_contract_start = validated_data.get('date_contract_start', instance.date_contract_start)
        instance.date_contract_end = validated_data.get('date_contract_end', instance.date_contract_end)
        instance.remark = validated_data.get('remark')
        instance.save()

        return instance


class CompanyIpListSerializer(serializers.ModelSerializer):
    company = serializers.SlugRelatedField(slug_field='uuid', queryset=Company.objects.all(), read_only=False,
                                           required=False)

    def validate(self, value):
        ip_count = CompanyIpList.objects.filter(company__uuid=value['company'].uuid).count()
        if ip_count >= settings.IP_WHITELIST_COUNT:
            raise ValidationError('IP whitelist count exceeded the limit.', code='invalid')
        return value

    class Meta:
        model = CompanyIpList
        fields = '__all__'