# shramo/views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Worker, Employer, Job, JobApplication
from .serializers import WorkerSerializer, EmployerSerializer, JobSerializer, JobApplicationSerializer
from rest_framework import status

class WorkerViewSet(viewsets.ModelViewSet):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer
    lookup_field = 'phone'

class EmployerViewSet(viewsets.ModelViewSet):
    queryset = Employer.objects.all()
    serializer_class = EmployerSerializer
    lookup_field = 'phone'

# shramo/views.py
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

    # ✅ Employer history (completed jobs only)
    @action(detail=False, methods=["get"])
    def employer_history(self, request):
        employer_phone = request.query_params.get("employer_phone")
        if not employer_phone:
            return Response({"error": "employer_phone required"}, status=status.HTTP_400_BAD_REQUEST)

        jobs = Job.objects.filter(employer_phone=employer_phone, status="completed")
        serializer = self.get_serializer(jobs, many=True)
        return Response(serializer.data)

    # ✅ Worker history (completed jobs only)
    @action(detail=False, methods=["get"])
    def worker_history(self, request):
        worker_phone = request.query_params.get("worker_phone")
        if not worker_phone:
            return Response({"error": "worker_phone required"}, status=status.HTTP_400_BAD_REQUEST)

        # fetch completed applications for this worker
        applications = JobApplication.objects.filter(
            worker_phone__phone=worker_phone,
            status="completed"
        ).select_related("job")

        jobs = [app.job for app in applications if app.job.status == "completed"]
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
    

    @action(detail=False, methods=["get"])
    def get_by_job_and_worker(self, request):
        job_id = request.query_params.get("job_id")
        worker_phone = request.query_params.get("worker_phone")

        if not job_id or not worker_phone:
            return Response({"error": "job_id and worker_phone required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            application = JobApplication.objects.get(job__id=job_id, worker_phone__phone=worker_phone)
            return Response(JobApplicationSerializer(application).data, status=status.HTTP_200_OK)
        except JobApplication.DoesNotExist:
            return Response({"application": None}, status=status.HTTP_200_OK)


    # Employer accepts worker
    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        application = self.get_object()
        application.employer_accept = True
        application.status = "waiting_for_worker_confirmation"
        application.save()

        # ✅ Update worker availability
        worker = application.worker
        worker.is_available = False
        worker.save()

        # If both accepted → assign job
        if application.worker_accept and application.employer_accept:
            application.status = "accepted"
            application.job.status = "assigned"
            application.job.save()
            application.save()

        return Response({"message": "Worker accepted", "status": application.status})

    # Worker accepts job
    @action(detail=True, methods=["post"])
    def worker_accept(self, request, pk=None):
        application = self.get_object()
        application.worker_accept = True
        application.status = "waiting_for_employer_confirmation"
        application.save()

        # ✅ Update worker availability
        worker = application.worker
        worker.is_available = False
        worker.save()

        # If employer already accepted → mark job assigned
        if application.worker_accept and application.employer_accept:
            application.status = "accepted"
            application.job.status = "assigned"
            application.job.save()
            application.save()

        return Response({"message": "Worker confirmed job", "status": application.status})

    # Mark job complete (by worker or employer)
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

        application.save()

        # 🔹 If both completed → mark job and free worker
        if application.worker_complete and application.employer_complete:
            application.status = "completed"
            application.job.status = "completed"
            application.job.save()

            worker = application.worker
            worker.is_available = True
            worker.save()
            application.save()

        return Response({"message": "Completion updated", "status": application.status})