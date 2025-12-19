from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # автентифікація та головна сторінка
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='cryptix_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('', views.home, name='home'),

    # користувачі та друзі
    path('users/', views.users_list, name='users_list'),
    path('friends/', views.friends_list, name='friends_list'),
    path('friend-requests/', views.friend_requests, name='friend_requests'),
    path('send-request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('accept-request/<int:friendship_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('reject-request/<int:friendship_id>/', views.reject_friend_request, name='reject_friend_request'),
    path('remove-friend/<int:user_id>/', views.remove_friend, name='remove_friend'),
    
    # підписники
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    path('followers/', views.followers_list, name='followers_list'),
    path('following/', views.following_list, name='following_list'),
    
    # чат
    path('conversations/', views.conversations_list, name='conversations_list'),
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('start-conversation/<int:user_id>/', views.start_conversation, name='start_conversation'),
]