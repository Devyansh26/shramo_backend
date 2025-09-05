# shramo/models.py
from django.db import models

class Worker(models.Model):
    phone = models.CharField(max_length=15, primary_key=True)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    skills = models.CharField(max_length=500)  # comma separated
    is_available = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)

    class Meta:
        db_table = 'workers'

class Employer(models.Model):
    phone = models.CharField(max_length=15, primary_key=True)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)

    class Meta:
        db_table = 'employers'

class Job(models.Model):
    employer_phone = models.ForeignKey(
        Employer,
        on_delete=models.CASCADE,
        to_field='phone',
        db_column='employer_phone'
    )
    work_type = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    work_date = models.DateField()
    wage = models.DecimalField(max_digits=8, decimal_places=2)
    detail = models.CharField(max_length=200)

    status = models.CharField(
        max_length=20,
        choices=[('open', 'open'), ('assigned', 'assigned'), ('completed', 'completed')],
        default='open'
    )

    created_at = models.DateTimeField(auto_now_add=True, null=True)  # 👈 important

    class Meta:
        db_table = 'jobs'

    def __str__(self):
        return f"{self.work_type} - {self.location} ({self.status})"
    


class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    worker_phone = models.ForeignKey(
        Worker,
        on_delete=models.CASCADE,
        to_field='phone',
        db_column='worker_phone'
    )

    # ✅ Confirmation flags
    worker_accept = models.BooleanField(default=False)      # worker agrees to take the job
    employer_accept = models.BooleanField(default=False)    # employer selects this worker

    # ✅ Completion flags
    worker_complete = models.BooleanField(default=False)    # worker marks job done
    employer_complete = models.BooleanField(default=False)  # employer marks job done

    # ✅ Derived status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'pending'),     # worker applied
            ('accepted', 'accepted'),   # employer accepted worker
            ('declined', 'declined'),   # employer declined worker
            ('completed', 'completed')  # both marked complete
        ],
        default='pending'
    )

    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'job_applications'
        unique_together = ('job', 'worker_phone')  # one application per worker per job

    def __str__(self):
        return f"Job {self.job.id} - Worker {self.worker_phone} ({self.status})"


class JobContact(models.Model):
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        db_column='job_id'
    )
    worker_phone = models.ForeignKey(
        Worker,
        on_delete=models.CASCADE,
        to_field='phone',
        db_column='worker_phone'
    )
    contacted_at = models.DateTimeField(auto_now_add=True)
    response = models.CharField(
        max_length=20,
        choices=[('accepted', 'accepted'), ('rejected', 'rejected'), ('no_response', 'no_response')],
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'job_contacts'
        unique_together = ('job', 'worker_phone')