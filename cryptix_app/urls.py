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
    
    # групи
    path('groups/', views.groups_list, name='groups_list'),
    path('group/create/', views.group_create, name='group_create'),
    path('group/<int:group_id>/', views.group_detail, name='group_detail'),
    path('group/<int:group_id>/join/', views.group_join, name='group_join'),
    path('group/<int:group_id>/leave/', views.group_leave, name='group_leave'),
    path('group/<int:group_id>/delete/', views.group_delete, name='group_delete'),
    path('post/<int:post_id>/comment/', views.group_post_comment, name='group_post_comment'),
    
    # профілі користувачів
    path('user/<str:username>/', views.user_profile_view, name='user_profile_view'),

    # сповіщення
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notification/<int:notification_id>/delete/', views.notification_delete, name='notification_delete'),
    
    # відгуки
    path('review/<str:username>/', views.leave_review, name='leave_review'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
]