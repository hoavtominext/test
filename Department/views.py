from django.shortcuts import render
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response

from Auth.views import TokenHasScopeForMethod
from .models import Department
from .serializers import DeparmentListSerializer


# Create your views here.

class DepartmentList(ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DeparmentListSerializer
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'GET': ['admin', 'coacha_admin']}

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response({"data": serializer.data, 'code': 200})

        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data, 'code': 200})


department_list = DepartmentList.as_view()
