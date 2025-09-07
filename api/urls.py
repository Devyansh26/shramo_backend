# shramo/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkerViewSet, EmployerViewSet, JobViewSet, JobApplicationViewSet,JobContactViewSet,BookingViewSet

router = DefaultRouter()
router.register(r'workers', WorkerViewSet, basename='worker')
router.register(r'employers', EmployerViewSet, basename='employer')
router.register(r'jobs', JobViewSet, basename='job')
router.register(r'job-applications', JobApplicationViewSet, basename='jobapplication')
router.register(r'job-contacts', JobContactViewSet, basename='jobcontact')
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('', include(router.urls)),
]
