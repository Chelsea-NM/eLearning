# I wrote this code
from django.db import models
from django.contrib.auth.models import User,Group
from django.utils.timezone import now
from .utils import Status,UserContactStatus,CourseMaterialType
# Create your models here.
class UserProfile(models.Model):
    profile_id = models.AutoField(primary_key=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=Status.choices(), default=Status.Active)
    dob = models.DateField(default=None, blank=True, null=True)
    occupation = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=255, blank=True)
    profile_picture = models.ImageField(upload_to='images/', blank=True)

    def __str__(self):
        return self.created_by

class UserContact(models.Model):
    contact_id = models.AutoField(primary_key=True)
    created_date = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=UserContactStatus.choices(), default=UserContactStatus.Invited)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,related_name="creator")
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="friend")

    def __str__(self):
        return self.created_by    
   
class UserStatus(models.Model):
    user_status_id = models.AutoField(primary_key=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_by_username = models.CharField(max_length=255, blank=True)
    message = models.CharField(max_length=255, blank=True)
    media_image = models.ImageField(upload_to='images/posts/', blank=True)
    
    def __str__(self):
        return self.created_by
    
class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    modified_date = models.DateTimeField(null=True)
    status = models.IntegerField(choices=Status.choices(), default=Status.Active)
    title = models.CharField(max_length=255, blank=False)
    description = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=255, blank=False)
    due_date = models.DateTimeField(null=True)
    
class CourseMaterial(models.Model):
    course_material_id = models.AutoField(primary_key=True)
    created_date = models.DateTimeField(auto_now_add=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.IntegerField(choices=Status.choices(), default=Status.Active)
    type = models.IntegerField(choices=CourseMaterialType.choices(), default=CourseMaterialType.Generic)
    title = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)    
    file_name = models.FileField(upload_to='images/course/material/', blank=True)   
    def __str__(self):
        return self.created_by
    
class CourseFeedback(models.Model):
    course_feedback_id = models.AutoField(primary_key=True)
    created_date = models.DateTimeField(auto_now_add=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_by_username = models.CharField(max_length=255, blank=True)
    status = models.IntegerField(choices=Status.choices(), default=Status.Active)
    message = models.CharField(max_length=255, blank=True)    

    def __str__(self):
        return self.created_by

class UserCourse(models.Model):
    user_course_id = models.AutoField(primary_key=True)
    created_date = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=Status.choices(), default=Status.Active)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,related_name="usercoursecreator")
    course = models.ForeignKey(Course, on_delete=models.CASCADE,related_name="course")
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="usercourse")
    def __str__(self):
        return self.created_by   
    
class Alert(models.Model):
    alert_id = models.AutoField(primary_key=True)
    created_date = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=Status.choices(), default=Status.Active)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255, blank=True)    
    
    def __str__(self):
        return self.created_by 
# end of code I wrote