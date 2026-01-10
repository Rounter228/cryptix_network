from django.contrib import admin
from .models import (Friendship, Follow, Conversation, Message, Group, 
                     GroupMembership, GroupPost, GroupPostComment, Notification, Review)

@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user', 'status', 'created_at']
    list_filter = ['status', 'created_at']

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['follower', 'following', 'created_at']

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'updated_at']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'conversation', 'content', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'creator', 'is_private', 'created_at']
    list_filter = ['is_private', 'created_at']

@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'group', 'role', 'joined_at']
    list_filter = ['role', 'joined_at']

@admin.register(GroupPost)
class GroupPostAdmin(admin.ModelAdmin):
    list_display = ['author', 'group', 'content', 'created_at']
    list_filter = ['created_at']

@admin.register(GroupPostComment)
class GroupPostCommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'content', 'created_at']
    list_filter = ['created_at']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'sender', 'notification_type', 'text', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['text', 'recipient__username', 'sender__username']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'reviewed_user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['reviewer__username', 'reviewed_user__username', 'comment']