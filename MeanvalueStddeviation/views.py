from django.shortcuts import render

# Create your views here.
from django.utils.datastructures import MultiValueDictKeyError
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from tablib import Dataset

from Auth.views import TokenHasScopeForMethod
from MeanvalueStddeviation.models import MeanvalueStddeviation
from MeanvalueStddeviation.resources import MeanvalueStddeviationResource
from MeanvalueStddeviation.serializers import MeanvalueStddeviationSerializer


class MeanvalueStddeviationImport(CreateAPIView):
    serializer_class = MeanvalueStddeviationSerializer
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'POST': ['user','admin', 'coacha_admin']}

    '''
        Import MeanvalueStddeviation
    '''

    def post(self, request, *args, **kwargs):
        try:
            meanvalue_stddeviation_csv = request.FILES['meanvalue_stddeviation_csv']
        except MultiValueDictKeyError:
            meanvalue_stddeviation_csv = False

        # email = request.data['email']
        if meanvalue_stddeviation_csv is False:
            data = {
                'data': {'message': 'meanvalue_stddeviation_csv not found'},
                'code': status.HTTP_403_FORBIDDEN
            }
            return Response(data, status=status.HTTP_403_FORBIDDEN)

        user_resource = MeanvalueStddeviationResource()
        dataset = Dataset()

        imported_data = dataset.load(meanvalue_stddeviation_csv.read().decode('utf-8'), format='csv')
        result = user_resource.import_data(dataset, dry_run=True)  # Test the data import
        if not result.has_errors():
            user_resource.import_data(dataset, dry_run=False)

        queryset = MeanvalueStddeviation.objects.all()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data, 'code': status.HTTP_200_OK}, status=status.HTTP_200_OK)


meanvalue_stddeviation_import = MeanvalueStddeviationImport.as_view()
