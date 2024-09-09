# I wrote this code

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import HttpResponseRedirect
from .forms import NameForm,UserProfileForm,UserProfilePictureForm,NewCourseForm,NewCourseMaterialForm
from eLearning_api.models import UserProfile, UserStatus, UserContact,Course,CourseMaterial, UserCourse,Alert
from eLearning_api.utils import Status,CourseMaterialType
from django.db.models import Q

# Create your views here. 
def home(request, user_id=0):
    user = request.user    
    if user.is_active:    
        # owner_user is the user who's homepage is being viewed        
        owner_user = user
        if user_id != 0:
            owner_user = User.objects.get(id=user_id)
            if not owner_user:
                owner_user = user
            
        owner_user_profile = UserProfile.objects.get(created_by=owner_user)     
        current_user_profile = UserProfile.objects.get(created_by=user)     
        status_updates = UserStatus.objects.filter(created_by=owner_user).order_by('-created_date')    

        owner_usertype = 'Student'
        if owner_user.groups.filter(name='Teacher').exists():
            owner_usertype = 'Teacher'       
    
        current_is_teacher = False
        current_usertype = 'Student'
        if user.groups.filter(name='Teacher').exists():    
            current_usertype = 'Teacher'  
            current_is_teacher = True
        
        is_owner = False
        if user.id == owner_user.id:
            is_owner = True
            
        courses = []
        if owner_usertype == 'Student':
            usercourses = UserCourse.objects.select_related("course").filter(~Q(status=Status.Archived),user=owner_user)
            for uc in usercourses:
                courses.append(uc.course)
        else:        
            usercourses = Course.objects.filter(~Q(status=Status.Archived),created_by=owner_user)
            for c in usercourses:
                courses.append(c)
                
        alert_list = []
        
        alerts = Alert.objects.filter(created_by=owner_user, status=Status.Active).order_by('-created_date') 
        for a in alerts:
            alert_list.append(a)
       
        return render(request, 'home.html', {'owner_user': owner_user,'owner_user_profile':owner_user_profile,'owner_usertype':owner_usertype, 'current_user': user,
                                             'current_usertype': current_usertype,'courses':courses, 'current_user_profile':current_user_profile,
                                             'status_updates': status_updates,'is_owner':is_owner,'current_is_teacher':current_is_teacher,'alert_list':alert_list})
        
    return HttpResponseRedirect('/signin')

def search_courses(request):  
    if not request.user.is_active: 
        return HttpResponseRedirect('/signin')   
     
    user = request.user
    current_is_teacher = False
    owner_user_profile = UserProfile.objects.get(created_by=user) 
    usertype = 'Student'
    if user.groups.filter(name='Teacher').exists():
        usertype = 'Teacher'       
        current_is_teacher = True
    if user.is_active:      
        return render(request, 'search_courses.html', {'user': user,'usertype': usertype,'current_is_teacher':current_is_teacher,
                                                       'owner_user_profile':owner_user_profile,'current_user_profile':owner_user_profile,'current_user':user})
        
    return HttpResponseRedirect('/signin')

def chat_room(request,course_id=0):
    if not request.user.is_active: 
        return HttpResponseRedirect('/signin')  
    
    if course_id == 0:
        return render(request, 'error.html', {'type': 'permissiondenied', 'message': 'Could not find chat room'})  
    
    course = Course.objects.get(course_id=course_id)    
    if not course:
        return render(request, 'error.html', {'type': 'permissiondenied', 'message': 'Could not find chat room'})  
    
    user = request.user
    if user.is_active:      
        return render(request, 'chat_room.html', {'course':course,'current_user':user})
        
    return HttpResponseRedirect('/')

def add_course(request): 
    if not request.user.is_active: 
        return HttpResponseRedirect('/signin')     
    # check if the current user has permission to update this profile
    current_user = request.user
    owner_user_profile = UserProfile.objects.get(created_by=current_user)
    errors = False
    
    if current_user.groups.filter(name='Student').exists():
        return render(request, 'error.html', {'type': 'permissiondenied', 'message': 'You do not have permission to view this page'})       

    if request.method == 'POST':

        form = NewCourseForm(request.POST, request.FILES)      
        
        if request.POST['title'] == '':
            errors = True
            
        if request.POST['category'] == '':
            errors = True
        
        if not errors:                
            if form.is_valid():            
                form_title = form.cleaned_data['title']
                form_description = form.cleaned_data['description']
                form_category = form.cleaned_data['category']
                form_duedate = form.cleaned_data['due_date']                
                course = Course(title=form_title,description=form_description,category=form_category,due_date=form_duedate,created_by=current_user)
                course.save()
                return HttpResponseRedirect('/course/'+str(course.course_id))
        
        return render(request, 'course_add_update.html', {'form': form,'user':current_user, 'title': request.POST['title'], 'description': request.POST['description'],
                                                              'category':request.POST['category'],'due_date':request.POST['due_date'],'current_is_teacher':True,
                                                              'owner_user_profile':owner_user_profile,'errors':errors,'form_type':'add','current_user_profile':owner_user_profile})   
        
    form = NewCourseForm()    
    return render(request, 'course_add_update.html', {'form': form,'current_user':current_user,'user':current_user, 'title': '', 'description': '','category':'','due_date':'',
                                                      'current_is_teacher':True,'owner_user_profile':owner_user_profile,'errors':errors,'form_type':'add','current_user_profile':owner_user_profile})

def add_course_material(request,course_id=0):

    if not request.user.is_active: 
        return HttpResponseRedirect('/signin')  

    if course_id == 0:
        return render(request, 'error.html', {'type': 'permissiondenied', 'message': 'Could not find course'})  
    
    course = Course.objects.get(course_id=course_id)     
    errors = False
    
    if course is None:
        return render(request, 'error.html', {'type': 'permissiondenied', 'message': 'Could not find course'})  
    
    if course.status == Status.Archived:
        return render(request, 'error.html', {'type': 'permissiondenied', 'message': 'That course has been archived or due date has been expired'}) 

    current_user = request.user    
    owner_user = course.created_by         
    file_uploaded = False
    owner_user_profile = UserProfile.objects.get(created_by=current_user)
    # check if the current user has permission to add course meterial
    if current_user.id != owner_user.id:
        return render(request, 'error.html', {'type': 'permissiondenied', 'message': 'You do not have permission to view this page'})

    if current_user.groups.filter(name='Student').exists():
        return render(request, 'error.html', {'type': 'permissiondenied', 'message': 'You do not have permission to view this page'})    

    if request.method == 'POST':

        form = NewCourseMaterialForm(request.POST, request.FILES)
        
        if request.POST['title'] == '':
            errors = True
            
        if request.FILES.get('file_name', False) == False:
            errors = True
        else:
            file_uploaded = True
        
        if not errors:   
            if form.is_valid():            
                form_title = form.cleaned_data['title']
                form_description = form.cleaned_data['description']
                filename = None        
            
                if request.FILES.get('file_name', False):
                    filename = request.FILES['file_name']
            
                coursematerial = CourseMaterial(title=form_title,description=form_description,file_name=filename,created_by=owner_user,course=course)
                coursematerial.save()
                
                courseusers = UserCourse.objects.select_related("user").filter(~Q(status=Status.Archived),course=course).order_by('-created_date') 
                for cu in courseusers:
                    alert = Alert(created_by=cu.user, status='10',message='New course material has been added to '+course.title)
                    alert.save()                         

                return HttpResponseRedirect('/course/'+str(course_id))
        else:
            return render(request, 'course_add_material.html', {'form': form,'user':current_user, 'title': request.POST['title'], 'description': request.POST['description'],
                                                                'filename':'','errors':errors,'file_uploaded':file_uploaded,'current_user_profile':owner_user_profile})   
        
    form = NewCourseMaterialForm()    
    return render(request, 'course_add_material.html', {'form': form,'user':current_user, 'title': '', 'description': '','filename':'','errors':errors,
                                                        'file_uploaded':file_uploaded,'current_user':current_user,'current_user_profile':owner_user_profile})

def view_course(request, course_id=0):  

    if not request.user.is_active: 
        return HttpResponseRedirect('/signin')  
    
    if course_id == 0:
        return render(request, 'error.html', {'type': 'permissiondenied', 'message': 'Could not find course'})  
    
    course = Course.objects.get(course_id=course_id) 
    
    if course is None:
        return render(request, 'error.html', {'type': 'permissiondenied', 'message': 'Could not find course'})  
    
    if course.status == Status.Archived:
        return render(request, 'error.html', {'type': 'permissiondenied', 'message': 'That course has been archived or due date has been expired'})  
 
    user = request.user  
    owner_user = course.created_by     
    owner_user_profile = UserProfile.objects.get(created_by=owner_user)     
    current_user_profile = UserProfile.objects.get(created_by=user)   

    owner_usertype = 'Student'
    if owner_user.groups.filter(name='Teacher').exists():
        owner_usertype = 'Teacher'       
    
    current_is_teacher = False
    current_usertype = 'Student'
    if user.groups.filter(name='Teacher').exists():    
        current_usertype = 'Teacher'  
        current_is_teacher = True
        
    is_owner = False
    if user.id == owner_user.id:
        is_owner = True
        
    course_material = CourseMaterial.objects.filter(course=course,status=Status.Active).order_by('-created_date')     
    usercourse = UserCourse.objects.filter(created_by=user, course=course)      
    is_enrolled = False  
    is_blocked= False      
    is_course_creator = False    
    if user == course.created_by:
        is_course_creator = True    
    
    if usercourse:      
        if usercourse.filter(status=Status.Blocked):            
            is_blocked = True
            is_enrolled = False
        else:
            is_enrolled = True
        
    if is_owner:
        is_enrolled = True
        
    course_students = []
    courseusers = UserCourse.objects.select_related("user").filter(~Q(status=Status.Archived),course=course).order_by('-created_date') 
    for cu in courseusers:
        status = "Active"
        cu_is_blocked = False
        if cu.status == Status.Blocked:
            status = 'Blocked'     
            cu_is_blocked = True  
                 
        course_student = {'id':cu.created_by.id,'username':cu.user.username, 'status':status,'is_blocked':cu_is_blocked, 'user_course_id':cu.user_course_id}
        course_students.append(course_student) 

    if user.is_active:      
        return render(request, 'course_view.html', {'owner_user': owner_user,'owner_user_profile':owner_user_profile,'owner_usertype':owner_usertype, 'current_user': user,
                      'current_usertype': current_usertype,'current_user_profile':current_user_profile,'is_owner':is_owner,'course':course,
                      'course_material':course_material,'current_is_teacher':current_is_teacher,'is_enrolled':is_enrolled,'usercourse':usercourse,
                      'is_course_creator':is_course_creator,'course_students':course_students,'is_blocked':is_blocked})
        
    return HttpResponseRedirect('/signin')

def my_courses(request):
    if not request.user.is_active: 
        return HttpResponseRedirect('/signin')  
    user = request.user
    courses = None
    current_is_teacher = False
    usertype = 'Student'
    if user.groups.filter(name='Teacher').exists():
        usertype = 'Teacher'     
        current_is_teacher = True  
        courses = Course.objects.filter(created_by=user).order_by('-created_date')  
    else:
        courses = []
        usercourses = UserCourse.objects.select_related("course").filter(~Q(status=Status.Archived),user=user)
        for uc in usercourses:
            courses.append(uc.course)      
   
    owner_user_profile = UserProfile.objects.get(created_by=user) 

    if user.is_active:      
        return render(request, 'user_courses.html', {'user': user, 'current_user': user,'usertype': usertype,'current_is_teacher':current_is_teacher,
                                                     'courses':courses,'owner_user_profile':owner_user_profile,'current_user_profile':owner_user_profile})
        
    return HttpResponseRedirect('/signin')

def users_list(request):
    if not request.user.is_active: 
        return HttpResponseRedirect('/signin')  
    user = request.user    
    if user.groups.filter(name='Student').exists():
        return render(request, 'error.html', {'type': 'permissiondenied', 'message': 'You do not have permission to view this page'})  
        
    owner_user_profile = UserProfile.objects.get(created_by=user)      
    user_data = []        
    users = User.objects.all().order_by('username')
    
    for u in users:
        if u.id != user.id:
            user_profile = UserProfile.objects.get(created_by=u)
            usertype = 'Student'
            if u.groups.filter(name='Teacher').exists():
                usertype = 'Teacher' 
            user_obj = {'id':u.id,'username':u.username,'firstname':u.first_name,'lastname':u.last_name,'usertype': usertype,'profile_picture':user_profile.profile_picture}
            user_data.append(user_obj) 

    if user.is_active:      
        return render(request, 'users_list.html', {'user': u, 'current_user': u,'users': user_data,'current_is_teacher':True,'owner_user_profile':owner_user_profile,'current_user_profile':owner_user_profile})
        
    return HttpResponseRedirect('/signin')

def error(request, message='', title=''):
    return render(request, 'error.html', {'message': message,'title':''})

def view_user_profile(request, user_id=0):
    if user_id == 0:
        return HttpResponseRedirect('/signin')

    current_user = request.user
    owner_user_profile = UserProfile.objects.get(created_by=current_user) 
    current_is_teacher = False
    if current_user.groups.filter(name='Teacher').exists():
        current_is_teacher = True 

    user = User.objects.filter(pk=user_id)
    if user:
        is_owner = False
        is_friend = False
        is_invited = False
        is_invitee = False
        user_contact = None   
        user = User.objects.get(pk=user_id)
        user_profile = UserProfile.objects.get(created_by=user)
        status_updates = UserStatus.objects.filter(created_by=user).order_by('-created_date')    
        
        owner_usertype = 'Student'
        if user.groups.filter(name='Teacher').exists():
            owner_usertype = 'Teacher' 
  
        current_usertype = 'Student' 
        contact_id = ''

        if current_user:
            current_user_profile = UserProfile.objects.get(created_by=current_user)
            if current_user.groups.filter(name='Teacher').exists():    
                current_usertype = 'Teacher' 
            if user.id == current_user.id:
                is_owner = True                
       
    else:
        return render(request, 'error.html', {'message': 'That user does not exist','title': 'Oooops!'})                                    

    return render(request, 'user_profile.html', {'owner_user': user,'user': current_user, 'user_profile': user_profile,'current_user':current_user,'is_owner':is_owner,
                                                 'current_user_profile_pic':current_user_profile.profile_picture, 'profile_picture': user_profile.profile_picture,
                                                 'is_friend':is_friend,'usercontact':user_contact,'is_invited': is_invited, 'is_invitee':is_invitee,
                                                 'contact_id':contact_id,'posts':status_updates,'owner_usertype':owner_usertype,'current_usertype':owner_usertype,
                                                 'current_is_teacher':current_is_teacher,'owner_user_profile':owner_user_profile})

def update_user_profile(request, user_id=0):
    if user_id == 0:
        return render(request, 'profile_update_details.html')

    user = User.objects.get(pk=user_id)
    user_profile = UserProfile.objects.get(created_by=user)  

    # check if the current user has permission to update this profile
    current_user = request.user
    if user.id != current_user.id:
        return render(request, 'error.html', {'type': 'permissiondenied', 'message': 'You do not have permission to view this page'})

    current_is_teacher = False
    if user.groups.filter(name='Teacher').exists():
            current_is_teacher = True 
            
    if request.method == 'POST':

        form = UserProfileForm(request.POST, request.FILES)
        # console.log('form: '+form)
        if form.is_valid():
            user.first_name = request.POST['firstname']
            user.last_name = request.POST['lastname']
            user.email = request.POST['email']
            user.save()
            
            user_profile.dob = form.cleaned_data['dob']
            user_profile.occupation = form.cleaned_data['occupation']
            user_profile.location = form.cleaned_data['location']
            user_profile.save()
            return HttpResponseRedirect('/user/profile/'+str(user_id))
        else:
            return render(request, 'user_profile_update.html', {'form': form, 'user': user, 'user_profile': user_profile,'current_user':current_user,
                                                                'current_is_teacher':current_is_teacher,'owner_user_profile':user_profile,'current_user_profile':user_profile})
    else:
        form = UserProfileForm()
    return render(request, 'profile_update_details.html', {'form': form, 'user': user, 'user_profile': user_profile,'current_user':current_user,
                                                           'current_is_teacher':current_is_teacher,'owner_user_profile':user_profile,'current_user_profile':user_profile})

def update_course(request, course_id=0):
    
    
    if course_id == 0:
        return render(request, 'error.html', {'type': 'permissiondenied', 'message': 'Could not find course'})

    course = Course.objects.get(course_id=course_id)
    
    if not course:
        return render(request, 'error.html', {'type': 'permissiondenied', 'message': 'Could not find course'})  
    
    # check if the current user has permission to update this profile
    current_user = request.user
    if current_user != course.created_by:
        return render(request, 'error.html', {'type': 'permissiondenied', 'message': 'You do not have permission to view this page'})
    
    errors = False
    user_profile = UserProfile.objects.get(created_by=current_user) 
    owner_user_profile = UserProfile.objects.get(created_by=current_user)  
    current_is_teacher = False
    if current_user.groups.filter(name='Teacher').exists():
        current_is_teacher = True 
    
    form = NewCourseForm() 
    if request.method == 'POST':
        
        if request.POST['title'] == '':
            errors = True
            
        if request.POST['category'] == '':
            errors = True
        
        if not errors:                
            course.title = request.POST['title']
            course.description = request.POST['description']
            course.category = request.POST['category']            
            course.save()
            return HttpResponseRedirect('/course/'+str(course.course_id))
        else:
            return render(request, 'course_add_update.html', {'user': current_user, 'user_profile': user_profile,'owner_user_profile':owner_user_profile,
                                                                'current_user':current_user,'current_is_teacher':current_is_teacher,'owner_user_profile':user_profile,'current_user_profile':user_profile,'form_type':'update'})
    else:
        return render(request, 'course_add_update.html', {'form': form,'current_user':current_user,'user':current_user, 'title': course.title, 
                                                          'description': course.description,'category':course.category,'due_date':course.due_date,
                                                          'current_is_teacher':current_is_teacher,'owner_user_profile':owner_user_profile,'errors':errors,
                                                          'form_type':'update','current_user_profile':user_profile})
       
    

def update_user_profile_picture(request, user_id=0):
    if user_id == 0:
        return render(request, 'user_profile_update.html')

    user = User.objects.get(pk=user_id)
    user_profile = UserProfile.objects.get(created_by=user)

    # check if the current user has permission to update this profile
    current_user = request.user
    if user.id != current_user.id:
        return render(request, 'error.html', {'type': 'permissiondenied', 'message': 'You do not have permission to view this page','title': 'Access Denied'})

    current_is_teacher = False
    if user.groups.filter(name='Teacher').exists():
        current_is_teacher = True 
    
    if request.method == 'POST':

        form = UserProfilePictureForm(request.POST, request.FILES)
        # console.log('form: '+form)
        if form.is_valid():

            if request.FILES.get('profile_picture', False):
                user_profile.profile_picture = request.FILES['profile_picture']
            user_profile.save()
            return HttpResponseRedirect('/user/profile/'+str(user_id))
        else:
            return render(request, 'profile_update_profilepic.html', {'form': form, 'user': user, 'user_profile': user_profile, 'profile_picture': user_profile.profile_picture,'current_user':current_user,
                                                           'current_is_teacher':current_is_teacher,'owner_user_profile':user_profile,'current_user_profile':user_profile})
    else:
        form = UserProfilePictureForm()
        
    return render(request, 'profile_update_profilepic.html', {'form': form, 'user': user, 'user_profile': user_profile, 'profile_picture': user_profile.profile_picture,'current_user':current_user,
                                                           'current_is_teacher':current_is_teacher,'owner_user_profile':user_profile,'current_user_profile':user_profile})

def login_request(request):
    error_message = ""
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")
            else:
                error_message = "Invalid username or password."
        else:
            error_message = "Invalid username or password."
    form = AuthenticationForm()
    return render(request=request, template_name="signin.html", context={"login_form": form, "error": error_message})


def signup(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)      
        
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            
            form_email = form.cleaned_data['email']
            form_username = form.cleaned_data['username']
            form_password = form.cleaned_data['password']
            form_user_type = 1
            
            #if request.POST.get('radiousertype', None) == 'on':
            #    form_user_type = 2
            
            if request.POST.get('radiousertype') == "2":
                form_user_type = 2
            
            user = User.objects.filter(username=form_username)
            if user:
                # username has been taken
                form.errors = {'username':'Username has been taken'}
                return render(request, 'signup.html', {'form': form})
            else:
                # No backend authenticated the credentials
                user = User.objects.create_user(
                    form_username, form_email, form_password)

                userprofile = UserProfile(created_by=user, status='10')
                userprofile.save()
                
                group = Group.objects.get(id=form_user_type)
                
                user.groups.add(group)

                login(request, user)
            return redirect("home")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()       
        
    return render(request, 'signup.html', {'form': form})


def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("home")

# end of code I wrote