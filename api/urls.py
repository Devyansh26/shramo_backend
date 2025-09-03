# shramo/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkerViewSet, EmployerViewSet, JobViewSet, JobContactViewSet

router = DefaultRouter()
router.register(r'workers', WorkerViewSet, basename='worker')
router.register(r'employers', EmployerViewSet, basename='employer')
router.register(r'jobs', JobViewSet, basename='job')
router.register(r'job-contacts', JobContactViewSet, basename='jobcontact')

urlpatterns = [
    path('', include(router.urls)),
]