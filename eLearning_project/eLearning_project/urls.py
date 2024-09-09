# I wrote this code
"""
URL configuration for eLearning_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include 
from django.conf import settings
from rest_framework import routers, serializers, viewsets
from django.conf.urls.static import static
from eLearning_api import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'profiles', views.UserProfileViewSet)
router.register(r'createstatusupdate', views.CreateUserStatusViewSet, basename="createstatusupdate")
router.register(r'userstatuses', views.UserStatusViewSet, basename="userstatuses")
router.register(r'getuserslist', views.UserListViewSet, basename="getuserslist")
router.register(r'getcourses', views.CourseListViewSet, basename="getcourses")
router.register(r'usercourse', views.UserCourseViewSet, basename="usercourse")
router.register(r'coursefeedback', views.CourseFeedbackViewSet, basename="coursefeedback")
router.register(r'coursematerialdelete', views.CourseMaterialViewSet, basename="coursematerialdelete")
router.register(r'updateusercoursestatus', views.UpdateUserCourseStatus, basename="updateusercoursestatus")
urlpatterns = [
    path('', include("eLearning_web_app.urls")),   
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')), 
    path('admin/', admin.site.urls), 
]

# end of code I wrote
