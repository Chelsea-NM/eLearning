# I wrote this code
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.home, name='home'),
    path("error", views.error, name='error'),
    path("signin", views.login_request, name="login"),
    path('signup', views.signup, name='signup'),
    path("logout", views.logout_request, name="logout"),
    path("my-courses", views.my_courses, name='user_courses'),
    path("search-courses", views.search_courses, name='search_courses'),
    path("add-courses", views.add_course, name='add_courses'),
    path("users", views.users_list, name='users_list'),
    path("course/<int:course_id>", views.view_course, name="course"),
    path("course/<int:course_id>/update/", views.update_course, name="updatecourse"),
    path("course/<int:course_id>/material/add", views.add_course_material, name="add_course_material"),
    path("course/<int:course_id>/chat-room/", views.chat_room, name='chat_room'),
    path("user/profile/<int:user_id>", views.home, name="userprofile"),
    path("user/profile/<int:user_id>/update/details", views.update_user_profile, name="userprofileupdate"),
    path("user/profile/<int:user_id>/update/profilepicture", views.update_user_profile_picture, name="userprofileupdateprofilepic"),
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
# end of code I wrote