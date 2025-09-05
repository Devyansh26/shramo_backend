# shramo/views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Worker, Employer, Job, JobApplication
from .serializers import WorkerSerializer, EmployerSerializer, JobSerializer, JobApplicationSerializer

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



    

    # ✅ Employer can list only their jobs
    @action(detail=False, methods=["get"])
    def my_jobs(self, request):
        employer_phone = request.query_params.get("employer_phone")
        jobs = Job.objects.filter(employer_phone=employer_phone)
        serializer = self.get_serializer(jobs, many=True)
        return Response(serializer.data)

class JobApplicationViewSet(viewsets.ModelViewSet):
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer


    def get_queryset(self):
        queryset = super().get_queryset()
        job_id = self.request.query_params.get("job_id")
        if job_id:
            queryset = queryset.filter(job__id=job_id)  # Filter by Job ID
        return queryset
    

    # ✅ Worker applies for a job 
    @action(detail=False, methods=["post"]) 
    def apply(self, request):
        job_id = request.data.get("job")
        worker_phone = request.data.get("worker_phone")

        if not job_id or not worker_phone: 
           return Response({"error": "job and worker_phone required"}, status=400) 
        try: 
            job = Job.objects.get(id=job_id, status="open") 
        except Job.DoesNotExist:
            return Response({"error": "Job not available"}, status=404) 
        
        worker = Worker.objects.filter(phone=worker_phone, is_available=True).first() 
        
        if not worker:
            return Response({"error": "Worker not available"}, status=400) 
        application, created = JobApplication.objects.get_or_create( job=job, worker_phone=worker ) 
        
        return Response(JobApplicationSerializer(application).data)

    # ✅ Employer accepts worker
    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        application = self.get_object()
        application.employer_accept = True
        application.status = "accepted"
        application.worker_phone.is_available = False
        application.worker_phone.save()
        application.save()

        # 🔹 If worker already accepted too → mark job as assigned
        if application.worker_accept and application.employer_accept:
            application.job.status = "assigned"
            application.job.save()

        return Response({"message": "Worker accepted", "status": application.status})

    # ✅ Worker accepts job
    @action(detail=True, methods=["post"])
    def worker_accept(self, request, pk=None):
        application = self.get_object()
        application.worker_accept = True
        application.status = "accepted"
        application.worker_phone.is_available = False
        application.worker_phone.save()
        application.save()

        # 🔹 If employer already accepted too → mark job as assigned
        if application.worker_accept and application.employer_accept:
            application.job.status = "assigned"
            Worker.is_available= False
            application.job.save()

        return Response({"message": "Worker confirmed job", "status": application.status})

    # ✅ Mark complete (by worker or employer)
    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        role = request.data.get("role")
        application = self.get_object()

        if role == "employer":
            application.employer_complete = True
        elif role == "worker":
            application.worker_complete = True
        else:
            return Response({"error": "Invalid role"}, status=400)

        # 🔹 If both completed → mark application + job as completed
        if application.worker_complete and application.employer_complete:
            application.status = "completed"
            application.worker_phone.is_available = True
            application.worker_phone.save()
            application.job.status = "completed"
            application.job.save()

        application.save()
        return Response({"message": "Completion updated", "status": application.status})

