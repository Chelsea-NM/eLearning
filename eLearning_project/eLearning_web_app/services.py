# I wrote this code
import requests
from django.middleware.csrf import get_token
from django.contrib.auth.models import User
from eLearning_api.models import UserProfile
from django.utils.dateparse import parse_datetime
# this page contains functions to make API requests

def get_users_list(request, user_id):
    url = 'http://127.0.0.1:8000/api' 
    request_url = url + '/users/'
    params = {"csrfmiddlewaretoken": get_token(request),'user_id': user_id}
    r = requests.get(request_url, params=params)
    users = r.json()       

    return {'users_list': users}

def get_all_posts(request, current_user):
    url = 'http://127.0.0.1:8000/api' 
    request_url = url + '/posts/'
    params = {"csrfmiddlewaretoken": get_token(request)}
    r = requests.get(request_url, params=params)
    posts = r.json()
    post_list = []
    current_user_count = 0
    for post in posts:
        created_by = User.objects.filter(id=post['created_by'])
        if created_by:
            created_by = User.objects.get(id=post['created_by'])
            u_profile = UserProfile.objects.get(created_by=created_by.id)
            profile_pic_url = ""
            if u_profile.profile_picture:
                profile_pic_url = u_profile.profile_picture.url
                
            if created_by.id == current_user.id:
                current_user_count += 1
                
            created_date = parse_datetime(post['created_date'])
            post_obj = {'created_by_id':created_by.id,'created_date':created_date,'username':created_by.username,'profile_picture': profile_pic_url,
            'id':created_by.id,'message':post['message'],'media_image':post['media_image']}
            post_list.append(post_obj)
    return {'posts': post_list,'current_user_count':current_user_count}

# end of code I wrote