from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, CreateAPIView
from tablib import Dataset

from Auth.views import TokenHasScopeForMethod
from .models import Csaplus24Average, Csaplus24Coefficient
from rest_framework.response import Response
from .serializers import Csaplus24AverageSerializer, Csaplus24CoefficientSerializer
from .resources import Csaplus24AverageResource, Csaplus24CoefficientResource


class Csaplus24AverageImport(CreateAPIView):
    serializer_class = Csaplus24AverageSerializer
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'POST': ['coacha_admin']}

    '''
        Import Csaplus24Average csv
    '''

    def post(self, request, *args, **kwargs):
        try:
            csaplus24_average_csv = request.FILES['csaplus24_average_csv']
        except MultiValueDictKeyError:
            csaplus24_average_csv = False
        # email = request.data['email']
        if csaplus24_average_csv is False:
            data = {
                'data': {'message': 'csaplus24_average_csv not found'},
                'code': status.HTTP_403_FORBIDDEN
            }
            return Response(data, status=status.HTTP_403_FORBIDDEN)

        user_resource = Csaplus24AverageResource()
        dataset = Dataset()

        imported_data = dataset.load(csaplus24_average_csv.read().decode('utf-8'), format='csv')
        result = user_resource.import_data(dataset, dry_run=True)  # Test the data import
        if not result.has_errors():
            user_resource.import_data(dataset, dry_run=False)

        queryset = Csaplus24Average.objects.all()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data, 'code': status.HTTP_200_OK}, status=status.HTTP_200_OK)


class Csaplus24CoefficientImport(CreateAPIView):
    serializer_class = Csaplus24CoefficientSerializer
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'POST': ['coacha_admin']}

    '''
        Import Csaplus24Coefficient csv
    '''

    def post(self, request, *args, **kwargs):
        try:
            csaplus24_coefficient_csv = request.FILES['csaplus24_coefficient_csv']
        except MultiValueDictKeyError:
            csaplus24_coefficient_csv = False

        # email = request.data['email']
        if csaplus24_coefficient_csv is False:
            data = {
                'data': {'message': 'csaplus24_coefficient_csv not found'},
                'code': status.HTTP_403_FORBIDDEN
            }
            return Response(data, status=status.HTTP_403_FORBIDDEN)

        user_resource = Csaplus24CoefficientResource()
        dataset = Dataset()

        imported_data = dataset.load(csaplus24_coefficient_csv.read().decode('utf-8'), format='csv')
        result = user_resource.import_data(dataset, dry_run=True)  # Test the data import
        if not result.has_errors():
            user_resource.import_data(dataset, dry_run=False)

        queryset = Csaplus24Coefficient.objects.all()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data, 'code': status.HTTP_200_OK}, status=status.HTTP_200_OK)


csaplus24_coefficient_import = Csaplus24CoefficientImport.as_view()
csaplus24_average_import = Csaplus24AverageImport.as_view()
