from django.shortcuts import render

# Create your views here.
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework import status, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListCreateAPIView, GenericAPIView, CreateAPIView, DestroyAPIView
from rest_framework.permissions import AllowAny

from Auth.views import TokenHasScopeForMethod
from Company.models import Company
from Users.models import User, UserProfile
from .models import Workshop
from .serializers import WorkshopSerializer, ListWorkshopSerializer, ManyWorkshopSerializer
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from Workshop.models import UserWorkshop
class WorkshopList(GenericAPIView):
    serializer_class = ListWorkshopSerializer
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'GET': ['admin','coacha_admin']}
    '''
        Show all workshop
    '''

    def get(self, request, *args, **kwargs):
        try:
            company_id = request.GET['company_id']
            if not Company.objects.filter(pk=company_id).exists():
                raise ValidationError("会社は存在しません。")
        except:
            return Response({'detail': '入社が必要な会社', 'code': 403},
                            status=status.HTTP_403_FORBIDDEN)

        instance = self.request.user
        user_scope = str(instance.groups.first())
        if user_scope == 'admin':
            if int(instance.userprofile.company_id) != int(company_id):
                raise PermissionDenied('権限がありません')

        queryset = Workshop.objects.filter(company_id=company_id).order_by('-date_workshop')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data, 'code': 200}, status=status.HTTP_200_OK)


class WorkshopCreate(GenericAPIView):
    serializer_class = WorkshopSerializer
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'POST': ['admin','coacha_admin']}

    '''
        Create workshop api
    '''

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        company_id = request.data['company_id']

        instance = self.request.user
        user_scope = str(instance.groups.first())
        if user_scope == 'admin':
            if int(instance.userprofile.company_id) != int(company_id):
                raise PermissionDenied('権限がありません')

        if serializer.is_valid():
            serializer.save()
            workshops = Workshop.objects.filter(company_id=company_id)
            data = ListWorkshopSerializer(workshops, many=True ).data

            return Response({"data": data, 'code': 200}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_200_OK)


class CreateManyWorkshop(GenericAPIView):
    queryset = Workshop.objects.all()
    serializer_class = ManyWorkshopSerializer
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'POST': ['admin','coacha_admin']}

    '''
        Create many workshop api
    '''

    def post(self, request, *args, **kwargs):
        workshops = request.data
        serializer = self.get_serializer(data=workshops)
        if serializer.is_valid():
            serializer.save()
            company_id = request.data.get('company_id')
            workshops = Workshop.objects.filter(company_id=company_id)
            data = ListWorkshopSerializer(workshops, many=True ).data

            return Response({"data": data, 'code': 200}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_200_OK)


class WorkshopEdit(GenericAPIView):
    serializer_class = WorkshopSerializer
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'POST': ['admin','coacha_admin']}
    '''
        Update workshop api
    '''
    def get_object(self):
        obj = Workshop.objects.filter(pk=self.kwargs.get('pk')).first()
        return obj

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(),data=request.data)

        company_id = request.data.get('company_id')
        instance = self.request.user
        user_scope = str(instance.groups.first())
        if user_scope == 'admin':
            if int(instance.userprofile.company_id) != int(company_id):
                raise PermissionDenied('権限がありません')

        if serializer.is_valid():
            serializer.save()
            workshops = Workshop.objects.filter(company_id=company_id)
            data = ListWorkshopSerializer(workshops, many=True ).data

            return Response({"data": data, 'code': 200}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_200_OK)

class WorkshopDetail(GenericAPIView):
    serializer_class = ListWorkshopSerializer
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'GET': ['admin','coacha_admin']}

    def get_object(self):
        try:
            company_id = self.request.GET['company_id']
            if not Company.objects.filter(pk=company_id).exists():
                raise ValidationError("会社は存在しません。")
        except:
            return Response({'detail': '入社が必要な会社', 'code': 403},
                            status=status.HTTP_403_FORBIDDEN)
        obj = Workshop.objects.filter(pk=self.kwargs.get('pk'),company_id=company_id).first()
        return obj

    def get(self, request, *args, **kwargs):
        workshop = self.get_object()
        data = self.get_serializer(workshop).data
        return Response(data, status=status.HTTP_200_OK)


class WorkshopDelete(DestroyAPIView):
    serializer_class = WorkshopSerializer
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'DELETE': ['admin','coacha_admin']}

    def get_object(self):
        obj = Workshop.objects.filter(pk=self.kwargs.get('pk')).first()
        return obj

    def delete(self, request, *args, **kwargs):
        self.get_object().delete()
        data = {
            'is_delete': True,
        }
        return Response(data, status=status.HTTP_200_OK)

workshop_create = WorkshopCreate.as_view()
workshop_create_many = CreateManyWorkshop.as_view()
workshop_list = WorkshopList.as_view()
workshop_edit = WorkshopEdit.as_view()
workshop_detail = WorkshopDetail.as_view()
workshop_delete = WorkshopDelete.as_view()