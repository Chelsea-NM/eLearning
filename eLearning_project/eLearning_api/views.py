# I wrote this code
from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import viewsets, status, permissions
from .serializers import UserSerializer, UserProfileSerializer, UserContactSerializer,UserStatusSerializer,UserCourseSerializer,CourseSerializer,CourseFeedbackSerializer,CourseMaterialSerializer
from .models import UserProfile, UserContact,UserStatus,Course,CourseMaterial, UserCourse,CourseFeedback,Alert
from rest_framework.response import Response
from .utils import Status,UserContactStatus

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
class AlertViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Alert.objects.all().order_by('-created_date')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
class UserListViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows a user to get a list of users    
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['get', ]
    test_first_name = ""
    def list(self, request):
        user_id=request.GET.get('user_id')
        searchterm=request.GET.get('searchterm').lower()
        user = User.objects.filter(id=user_id)
        
        if user:   
       
            user_list = []                   
               
            users = User.objects.all().order_by('username')
            
            for u in users:

                usermatch = True
                if searchterm:     

                    usermatch = False
                    
                    if u.first_name.lower().find(searchterm) != -1:
                        usermatch = True                       
                            
                    if u.username.lower().find(searchterm) != -1:
                        usermatch = True
                        
                    if u.last_name.lower().find(searchterm) != -1:
                        usermatch = True
                        
                if str(u.id) == user_id:
                    usermatch = False

                if usermatch == True:
                    u_profile = UserProfile.objects.get(created_by=u) 
                    usertype = 'Student'
                    if u.groups.filter(name='Teacher').exists():
                        usertype = 'Teacher' 
                    
                    profile_pic_url = ""
                    if u_profile.profile_picture:
                        profile_pic_url = u_profile.profile_picture.url
                    else:
                        profile_pic_url = "/static/images/avatar.png"
                    
                        
                    u_obj = {'first_name':u.first_name,'last_name':u.last_name,'profile_picture':profile_pic_url,'date_joined':u.date_joined.strftime('%Y-%m-%d'),'username':u.username,
                                  'id':u.id,'usertype':usertype}
                    
                    user_list.append(u_obj) 
                

            user_list = tuple(user_list) 
            return Response(data={'users_list':user_list}, status=status.HTTP_200_OK)
        else:
            return Response(data={'error':'Failed to fetch user list'}, status=status.HTTP_304_NOT_MODIFIED)

class CourseListViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows a user to get a list of users    
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['get', ]
    def list(self, request):
        user_id=request.GET.get('user_id')
        searchterm=request.GET.get('searchterm').lower()
        user = User.objects.filter(id=user_id)
        
        if user:   
       
            course_lists = []                   
               
            courses = Course.objects.all().order_by('-created_date')
            
            for c in courses:

                usermatch = True
                if searchterm:     

                    usermatch = False
                    
                    if c.title.lower().find(searchterm) != -1:
                        usermatch = True                       
                            
                    if c.description.lower().find(searchterm) != -1:
                        usermatch = True
                        
                    if c.category.lower().find(searchterm) != -1:
                        usermatch = True                       

                if c.status != Status.Active:
                    usermatch = False
                print(usermatch)
                if usermatch == True:                   
             
                    u_obj = {'title':c.title,'description':c.description,'category':c.category,'course_id':c.course_id,'due_date':c.due_date}
                    
                    course_lists.append(u_obj) 
                

            course_lists = tuple(course_lists) 
            return Response(data={'courses_list':course_lists}, status=status.HTTP_200_OK)
        else:
            return Response(data={'error':'Failed to fetch courses'}, status=status.HTTP_304_NOT_MODIFIED)

class UserProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows user profiles to be viewed or edited.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]


class CourseFeedbackViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows course feedback to be viewed or created.
    """
    queryset = CourseFeedback.objects.all()
    serializer_class = CourseFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post','get']    
        
    def list(self, request):
        course_id=request.GET.get('course_id')
        course = Course.objects.get(course_id=course_id)
        if course:  
            course_feedback_list = []   
            course_feedback = CourseFeedback.objects.filter(course=course).order_by('-created_date')
            for cf in course_feedback:
                cf_obj = {'created_by_username':cf.created_by_username,'message': cf.message, 'created_date':cf.created_date, 'course_feedback_id':cf.course_feedback_id}
                course_feedback_list.append(cf_obj) 
                
            course_feedback_list = tuple(course_feedback_list) 
            return Response(data={'course_feedback_list':course_feedback_list}, status=status.HTTP_200_OK)
        else:
            return Response(data={'error':'Failed to fetch course feedback'}, status=status.HTTP_304_NOT_MODIFIED)
    
    def create(self, request, *args, **kwargs):
     
        data = {
            "created_by": request.POST.get('created_by_id', None),"message": request.POST.get('message', None),
            'course':request.POST.get('course_id', None),'created_by_username':request.POST.get('created_by_username', None)
        }        
            
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():                    
            try:
                serializer.save()
            except Exception as e:
                raise e
            
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CourseMaterialViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows course material to be deleted
    """

    queryset = CourseMaterial.objects.all()
    serializer_class = CourseMaterialSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post']
    
    def create(self, request, *args, **kwargs):
        user_id=request.POST.get('current_user_id')
        user = User.objects.filter(id=user_id)
        course_material_id=request.POST.get('course_material_id')
        coursematerial = CourseMaterial.objects.get(course_material_id=course_material_id)
        if coursematerial:  
            coursematerial.status = Status.Archived
            coursematerial.save()
            return Response(data={}, status=status.HTTP_200_OK)
        else:
            return Response(data={'error':'Failed to delete course material'}, status=status.HTTP_304_NOT_MODIFIED)
        
class UpdateUserCourseStatus(viewsets.ModelViewSet):
    """
    API endpoint that allows course owner to block or un-block enrolled students
    """

    queryset = UserCourse.objects.all()
    serializer_class = UserCourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post']
    
    def create(self, request, *args, **kwargs):
        action=request.POST.get('action')
        user_course_id=request.POST.get('user_course_id')
        usercourse = UserCourse.objects.get(user_course_id=user_course_id)
        alert_msg = 'Access to '+usercourse.course.title+' '
        if usercourse:  
            if action == 'block':
                usercourse.status = Status.Blocked
                alert_msg += 'blocked!'
            else:
                usercourse.status = Status.Active
                alert_msg += 'unblocked!'
            usercourse.save()
            alert = Alert(created_by=usercourse.user, status='10',message=alert_msg)
            alert.save()
            return Response(data={}, status=status.HTTP_200_OK)
        else:
            return Response(data={'error':'Failed to update course user status'}, status=status.HTTP_304_NOT_MODIFIED)

class UserContactViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows user contacts(friends) to be viewed or edited.
    """
    queryset = UserContact.objects.all()
    serializer_class = UserContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', ]
    
    def retrieve(self, request, pk=None):
        usercontact = self.get_object()
        serializer = self.get_serializer(usercontact)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CreateUserStatusViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to create a post.
    """
    queryset = UserStatus.objects.none()
    serializer_class = UserStatusSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post', ]

    def create(self, request, *args, **kwargs):
     
        data = {
            "created_by": request.POST.get('created_by_id', None),"message": request.POST.get('message', None),'created_by_username':request.POST.get('created_by_username', None)
        }        
            
        if request.FILES.get('media_image_file', False):
            data = {
            "created_by": request.POST.get('created_by_id', None),"message": request.POST.get('message', None),"media_image":request.FILES['media_image_file'],'created_by_username':request.POST.get('created_by_username', None)
            }  
            
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():                    
            try:
                serializer.save()
            except Exception as e:
                raise e
            
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
     
class UserCourseViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to get and create user course enrollments
    """
    queryset = UserCourse.objects.none()
    serializer_class = UserCourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post', ]

    def create(self, request, *args, **kwargs):

        data = {
            "created_by": request.POST.get('created_by_id', None),"course": request.POST.get('course_id', None),"user": request.POST.get('created_by_id', None)
        }        
       
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():                    
            try:
                usercourse = UserCourse.objects.filter(user=data['user'], course=data['course'])   
                #print(usercourse)
                if not usercourse:
                    serializer.save()                    
                    c = Course.objects.get(course_id=data['course'])
                    if c:
                        u = User.objects.get(pk=data['user'])
                        if u:
                            alert = Alert(created_by=c.created_by, status='10',message=u.username+' enrolled to '+c.title)
                            alert.save()
                            alert = Alert(created_by=u, status='10',message='Enrolled to '+c.title)
                            alert.save()
            except Exception as e:
                raise e
            
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
           
class UserStatusViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows a user to get posts
    """
    queryset = UserStatus.objects.all().order_by('-created_date')
    serializer_class = UserStatusSerializer
    http_method_names = ['get', ]
    
    def retrieve(self, request, pk=None):
        status_updates = self.queryset
        serializer = self.get_serializer(status_updates)
        # user = User.objects.get(pk=serializer.data['id'])
        # user_profile = UserProfile.objects.get(created_by=user)
        # data = {'username':user.username, 'user_profile':user_profile}
        # data.update(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# end of code I wrote
