from django.contrib import admin
from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView

class HealthView(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request):
        return Response({'status': 'ok', 'service': 'crm-api'})

urlpatterns = [path('admin/', admin.site.urls), path('api/health/', HealthView.as_view(), name='health')]
