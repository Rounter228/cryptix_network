from .models import Notification

def create_notification(recipient, notification_type, text, sender=None, link=''):
    Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type=notification_type,
        text=text,
        link=link
    )

def notify_friend_request(from_user, to_user):
    create_notification(
        recipient=to_user,
        sender=from_user,
        notification_type=Notification.FRIEND_REQUEST,
        text=f'{from_user.username} надіслав вам запит у друзі',
        link='/app/friend-requests/'
    )

def notify_friend_accept(from_user, to_user):
    create_notification(
        recipient=from_user,
        sender=to_user,
        notification_type=Notification.FRIEND_ACCEPT,
        text=f'{to_user.username} прийняв ваш запит у друзі',
        link=f'/app/user/{to_user.username}/'
    )

def notify_new_message(sender, recipient, conversation_id):
    create_notification(
        recipient=recipient,
        sender=sender,
        notification_type=Notification.MESSAGE,
        text=f'{sender.username} надіслав вам повідомлення',
        link=f'/app/conversation/{conversation_id}/'
    )

def notify_group_post(group, author):
    members = group.members.exclude(id=author.id)
    for member in members:
        create_notification(
            recipient=member,
            sender=author,
            notification_type=Notification.GROUP_POST,
            text=f'{author.username} створив новий пост в групі "{group.name}"',
            link=f'/app/group/{group.id}/'
        )

def notify_new_comment(post, comment_author):
    if post.author != comment_author:
        create_notification(
            recipient=post.author,
            sender=comment_author,
            notification_type=Notification.COMMENT,
            text=f'{comment_author.username} прокоментував ваш пост',
            link=f'/app/group/{post.group.id}/'
        )

def notify_new_review(reviewer, reviewed_user, rating):
    create_notification(
        recipient=reviewed_user,
        sender=reviewer,
        notification_type=Notification.REVIEW,
        text=f'{reviewer.username} залишив вам відгук ({rating}★)',
        link=f'/app/user/{reviewed_user.username}/'
    )