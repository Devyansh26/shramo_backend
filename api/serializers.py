# shramo/serializers.py
from rest_framework import serializers
from .models import Worker, Employer, Job, JobApplication,JobContact,Booking

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

class JobApplicationSerializer(serializers.ModelSerializer):
    worker = WorkerSerializer(source="worker_phone", read_only=True)
    worker_phone = serializers.CharField(write_only=True)

    class Meta:
        model = JobApplication
        fields = '__all__'
        read_only_fields = ('status', 'applied_at', 'updated_at', 'worker')

    # def get_derived_status(self, obj):
    #     if obj.status == "pending" and obj.employer_accept and not obj.worker_accept:
    #         return "waiting_for_worker_confirmation"
    #     return obj.status



class JobSerializer(serializers.ModelSerializer):
    applications = JobApplicationSerializer(many=True, read_only=True)

    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ('status', 'created_at')

    
class JobContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobContact
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    employer = EmployerSerializer(source="employer_phone", read_only=True)
    worker = WorkerSerializer(source="worker_phone", read_only=True)
    employer_phone = serializers.SlugRelatedField(
        queryset=Employer.objects.all(),
        slug_field='phone'
    )
    worker_phone = serializers.SlugRelatedField(
        queryset=Worker.objects.all(),
        slug_field='phone'
    )

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ('status', 'created_at')