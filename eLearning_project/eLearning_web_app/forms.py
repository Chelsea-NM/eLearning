# I wrote this code
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core import validators
from django.contrib.auth.validators import UnicodeUsernameValidator
from eLearning_api.models import UserProfile, UserStatus,Course, CourseMaterial

class NameForm(forms.Form):
    username = forms.CharField(label='Username', required=True, max_length=100,validators=[UnicodeUsernameValidator(message="Username invalid")])
    email = forms.CharField(label='Email', required=True, max_length=50,validators=[validators.EmailValidator(message="Email invalid")])
    password = forms.CharField(label='Password', required=True,min_length=5, max_length=20,widget=forms.PasswordInput())
    confirmpassword = forms.CharField(label='Confirm Password', required=True,min_length=5, max_length=20,widget=forms.PasswordInput())
    
    def clean(self):
        # perform additional validation for confirm password and checking if the username is available
        cd = self.cleaned_data
        if cd.get('password') != cd.get('confirmpassword'):
            self.add_error('confirmpassword', "Passwords do not match")
            
        user = User.objects.filter(username=cd.get('username'))    
        if user:
            self.add_error('username', "Username has been taken")    
                        
        return cd
    
class PostStatusUpdate(forms.Form):
	class Meta:
		model = UserStatus
		fields = ("message", "media_image")
    
class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)
	# iterable
	usertypes = (
	("Learner", "Learner"),
    ("Teacher", "Teacher")
	)
	group = forms.TypedChoiceField(required=True,choices = usertypes)
	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2","group")

	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user

class SignUpForm(UserCreationForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class SignInForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email address doesn't exist")
        return email

    def clean_password(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        user = User.objects.get(email=email)
        if not user.check_password(password):
            raise forms.ValidationError("Incorrect password")
        return password

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['dob', 'occupation', 'location']
        widgets = {
            'dob': forms.DateInput(
                attrs={'type': 'date', 'placeholder': '', 'class': 'form-control'}
            )
        }
        
class NewCourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'category','due_date']
        widgets = {
            'due_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'placeholder': '', 'class': 'form-control'}
            )
        }                

class NewCourseMaterialForm(forms.ModelForm):
    class Meta:
        model = CourseMaterial
        fields = ['title', 'description', 'file_name']


class UserProfilePictureForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture']
        
# end of code I wrote
