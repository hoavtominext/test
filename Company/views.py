from django.shortcuts import render
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.response import Response

from Auth.views import TokenHasScopeForMethod
from Users.models import User, UserProfile
from .models import Company
from .serializers import CompanyCreateSerializer, CompanySerializer, CompanyEditSerializer
# Create your views here.
from rest_framework.generics import CreateAPIView, GenericAPIView, DestroyAPIView


class CompanyPagination(LimitOffsetPagination, PageNumberPagination):
    default_limit = 20


class CompanyList(GenericAPIView):
    serializer_class = CompanySerializer
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'GET': ['coacha_admin']}
    pagination_class = CompanyPagination

    def get(self, request, *args, **kwargs):
        queryset = Company.objects.filter().order_by('-created_at')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data, 'code': 200})

class CompanyCreate(CreateAPIView):
    serializer_class = CompanyCreateSerializer
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'POST': ['coacha_admin']}

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            company = serializer.save()
            data = CompanyCreateSerializer(company).data
            return Response({"data": data, 'code': 200})

        return Response(serializer.errors, status=status.HTTP_200_OK)


class CompanyEdit(GenericAPIView):
    serializer_class = CompanyEditSerializer
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'POST': ['coacha_admin']}

    def get_object(self):
        obj = Company.objects.filter(pk=self.kwargs.get('pk')).first()
        return obj

    def post(self, request, *args, **kwargs):
        company_id = self.kwargs.get('pk')
        instance = self.request.user
        user_scope = str(instance.groups.first())
        if user_scope == 'admin':
            if int(instance.userprofile.company_id) != int(company_id):
                raise PermissionDenied('権限がありません')

        serializer = self.get_serializer(self.get_object(),data=request.data)
        if serializer.is_valid():
            company = serializer.save()
            data = CompanyEditSerializer(company).data
            return Response({"data": data, 'code': 200})

        return Response(serializer.errors, status=status.HTTP_200_OK)


class CompanyDetail(GenericAPIView):
    serializer_class = CompanySerializer
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'GET': ['admin','coacha_admin']}

    def get_object(self):
        obj = Company.objects.filter(pk=self.kwargs.get('pk')).first()
        return obj

    def get(self, request, *args, **kwargs):
        company_id = self.kwargs.get('pk')
        instance = self.request.user
        user_scope = str(instance.groups.first())
        if user_scope == 'admin':
            if int(instance.userprofile.company_id) != int(company_id):
                raise PermissionDenied('権限がありません')

        company = self.get_object()
        data = self.get_serializer(company).data
        return Response(data, status=status.HTTP_200_OK)

class CompanyDelete(DestroyAPIView):
    serializer_class = CompanySerializer
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'DELETE': ['coacha_admin']}

    def get_object(self):
        obj = Company.objects.filter(pk=self.kwargs.get('pk')).first()
        return obj

    def delete(self, request, *args, **kwargs):
        count = UserProfile.objects.filter(company_id=self.get_object().id).count()
        if count > 0:
            data = {
                'is_delete': False
            }
            return Response(data, status=status.HTTP_200_OK)

        for profile in UserProfile.objects.filter(company_id=self.get_object().id):
            user = User.objects.filter(pk=profile.user_id).first()
            user.delete()

        self.get_object().delete()
        data = {
            'is_delete': True,
        }
        return Response(data, status=status.HTTP_200_OK)

company_create = CompanyCreate.as_view()
company_list = CompanyList.as_view()
company_edit = CompanyEdit.as_view()
company_detail = CompanyDetail.as_view()
company_delete = CompanyDelete.as_view()
