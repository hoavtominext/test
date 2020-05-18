from django.shortcuts import render

# Create your views here.
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework import status
from rest_framework.generics import GenericAPIView, ListCreateAPIView
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.response import Response
from Auth.views import TokenHasScopeForMethod
from EmailPostLearningContent.models import EmailPostContent
from .serializers import MailMagazineSerializer, UpdateMailMagazineSerializer
from .models import MailMagazine


class UserPagination(LimitOffsetPagination, PageNumberPagination):
    default_limit = 20


class ListMailMagazine(ListCreateAPIView, LimitOffsetPagination):
    queryset = MailMagazine.objects.all()
    serializer_class = MailMagazineSerializer
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'GET': ['user','admin', 'coacha_admin']}
    pagination_class = UserPagination

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        count_send_email = 0
        try:
            mail_count = EmailPostContent.objects.get(user=request.user)
            count_send_email = mail_count.count_send_email
            queryset = queryset[:count_send_email]
        except EmailPostContent.DoesNotExist:
            queryset = queryset.none()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response({"data": serializer.data, "mail_count":count_send_email})

        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data, 'code': 200})


class CreateMailMagazine(GenericAPIView):
    serializer_class = MailMagazineSerializer
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'POST': ['coacha_admin']}

    def post(self, request, *args, **kwargs):
        serializer = MailMagazineSerializer(data=request.data)
        if serializer.is_valid():
            mail_magazine = serializer.save()
            data = MailMagazineSerializer(mail_magazine).data

            queryset = MailMagazine.objects.all().order_by('-id')
            serializer = self.get_serializer(queryset, many=True)
            return Response({"data": serializer.data, 'code': 200})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateMailMagazine(GenericAPIView):
    serializer_class = UpdateMailMagazineSerializer
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'POST': ['coacha_admin']}

    def get_object(self):
        pk = self.request.data['id']
        obj = MailMagazine.objects.filter(pk=pk).first()
        return obj

    def post(self, request, *args, **kwargs):
        serializer = UpdateMailMagazineSerializer(self.get_object(), data=request.data)
        if serializer.is_valid():
            mail_magazine = serializer.save()
            data = UpdateMailMagazineSerializer(mail_magazine).data

            queryset = MailMagazine.objects.all().order_by('-id')
            serializer = self.get_serializer(queryset, many=True)
            return Response({"data": serializer.data, 'code': 200})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DetailMailMagazine(GenericAPIView):
    serializer_class = MailMagazineSerializer
    queryset = MailMagazine.objects.all()
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'GET': ['user','admin', 'coacha_admin']}

    def get(self, request, pk, format=None):
        try:
            mail_magazine = MailMagazine.objects.get(pk=pk)
        except MailMagazine.DoesNotExist:
            return Response({"data": {
                'id':'Mail magazine not found'}, 'code': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

        serializer = MailMagazineSerializer(mail_magazine)
        return Response({"data": serializer.data, 'code': 200})

create_mail_magazine = CreateMailMagazine.as_view()
list_mail_magazine = ListMailMagazine.as_view()
detail_mail_magazine = DetailMailMagazine.as_view()
update_mail_magazine = UpdateMailMagazine.as_view()
