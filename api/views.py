# shramo/views.py
from rest_framework import viewsets
from .models import Worker, Employer, Job, JobContact
from .serializers import WorkerSerializer, EmployerSerializer, JobSerializer, JobContactSerializer

class WorkerViewSet(viewsets.ModelViewSet):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer
    lookup_field = 'phone'

class EmployerViewSet(viewsets.ModelViewSet):
    queryset = Employer.objects.all()
    serializer_class = EmployerSerializer
    lookup_field = 'phone'

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer

class JobContactViewSet(viewsets.ModelViewSet):
    queryset = JobContact.objects.all()
    serializer_class = JobContactSerializer