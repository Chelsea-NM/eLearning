
# I wrote this code
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile,UserContact,UserStatus,Course, CourseMaterial, UserCourse,CourseFeedback, Alert

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username','last_name','first_name', 'email','date_joined']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['profile_id', 'created_by', 'created_date', 'status', 'dob', 'occupation',
                  'location', 'profile_picture']
        
class UserContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserContact
        fields = ['contact_id', 'created_date', 'status','created_by', 'user']
        
class UserStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStatus
        fields = ['user_status_id', 'created_by', 'created_date', 'message', 'media_image']
        
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['course_id', 'created_date','course','created_by', 'modified_date', 'status', 'title', 'description', 'due_date']
        
class CourseMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseMaterial
        fields = ['course_material_id', 'created_date','course', 'created_by', 'status', 'type','title','description','file_name']        

class CourseFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseFeedback
        fields = ['course_feedback_id', 'created_date','course', 'created_by','created_by_username', 'status','message']
        
class UserCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCourse
        fields = ['user_course_id', 'created_date', 'created_by', 'status', 'course','user']
        
class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = ['alert_id', 'created_date', 'status','created_by', 'message']
# end of code I wrote


