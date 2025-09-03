# shramo/serializers.py
from rest_framework import serializers
from .models import Worker, Employer, Job, JobContact

class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = '__all__'
        read_only_fields = ('rating',)

class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = '__all__'
        read_only_fields = ('rating',)

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ('status', 'worker_phone')

class JobContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobContact
        fields = '__all__'
        read_only_fields = ('contacted_at',)