from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.contrib import messages
from django.utils import timezone
from .forms import RegisterForm, ProfileUpdateForm
from .models import Profile, Friendship, Follow, Conversation, Message


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'cryptix_app/register.html', {'form': form})

@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=profile)
    
    return render(request, 'cryptix_app/profile.html', {'form': form})

@login_required
def home(request):
    return render(request, 'cryptix_app/home.html')


# -- друзі та підписники --

@login_required
def users_list(request):
    query = request.GET.get('q', '')
    users = User.objects.exclude(id=request.user.id)
    
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )

    sent_requests = Friendship.objects.filter(from_user=request.user).values_list('to_user_id', 'status')
    received_requests = Friendship.objects.filter(to_user=request.user).values_list('from_user_id', 'status')
    
    sent_dict = dict(sent_requests)
    received_dict = dict(received_requests)
    
    following_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
    
    users_data = []
    for user in users:
        user_info = {
            'user': user,
            'friendship_status': sent_dict.get(user.id) or received_dict.get(user.id),
            'is_following': user.id in following_ids,
            'has_pending_request': received_dict.get(user.id) == 'pending'
        }
        users_data.append(user_info)
    
    return render(request, 'cryptix_app/users_list.html', {'users_data': users_data, 'query': query})


@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    
    if to_user == request.user:
        messages.error(request, 'Ви не можете надіслати запит самому собі')
        return redirect('users_list')
    
    friendship, created = Friendship.objects.get_or_create(
        from_user=request.user,
        to_user=to_user,
        defaults={'status': 'pending'}
    )
    
    if created:
        messages.success(request, f'Запит дружби надіслано користувачеві {to_user.username}')
    else:
        messages.info(request, 'Запит вже було надіслано')
    
    return redirect('users_list')


@login_required
def accept_friend_request(request, friendship_id):
    friendship = get_object_or_404(Friendship, id=friendship_id, to_user=request.user)
    friendship.status = 'accepted'
    friendship.save()
    messages.success(request, f'Ви тепер друзі з {friendship.from_user.username}')
    return redirect('friend_requests')


@login_required
def reject_friend_request(request, friendship_id):
    friendship = get_object_or_404(Friendship, id=friendship_id, to_user=request.user)
    friendship.delete()
    messages.success(request, 'Запит відхилено')
    return redirect('friend_requests')


@login_required
def remove_friend(request, user_id):
    user = get_object_or_404(User, id=user_id)
    Friendship.objects.filter(
        Q(from_user=request.user, to_user=user) |
        Q(from_user=user, to_user=request.user)
    ).delete()
    messages.success(request, f'{user.username} видален з друзів')
    return redirect('friends_list')


@login_required
def friend_requests(request):
    pending_requests = Friendship.objects.filter(
        to_user=request.user,
        status='pending'
    ).select_related('from_user')
    
    return render(request, 'cryptix_app/friend_requests.html', {'requests': pending_requests})


@login_required
def friends_list(request):
    friends_ids = Friendship.objects.filter(
        Q(from_user=request.user, status='accepted') |
        Q(to_user=request.user, status='accepted')
    ).values_list('from_user_id', 'to_user_id')
    
    friend_ids = set()
    for from_id, to_id in friends_ids:
        friend_ids.add(from_id if from_id != request.user.id else to_id)
    
    friends = User.objects.filter(id__in=friend_ids)
    
    return render(request, 'cryptix_app/friends_list.html', {'friends': friends})


@login_required
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    
    if user_to_follow == request.user:
        messages.error(request, 'Ви не можете підписатися на себе')
        return redirect('users_list')
    
    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=user_to_follow
    )
    
    if created:
        messages.success(request, f'Ви підписалися на {user_to_follow.username}')
    else:
        messages.info(request, 'Ви вже підписані на цього користувача')
    
    return redirect('users_list')


@login_required
def unfollow_user(request, user_id):
    user_to_unfollow = get_object_or_404(User, id=user_id)
    Follow.objects.filter(follower=request.user, following=user_to_unfollow).delete()
    messages.success(request, f'Ви відписались від {user_to_unfollow.username}')
    return redirect('users_list')


@login_required
def followers_list(request):
    followers = User.objects.filter(following__following=request.user)
    return render(request, 'cryptix_app/followers_list.html', {'followers': followers})


@login_required
def following_list(request):
    following = User.objects.filter(followers__follower=request.user)
    return render(request, 'cryptix_app/following_list.html', {'following': following})


# -- чат і повідомлення

@login_required
def conversations_list(request):
    conversations = request.user.conversations.all().prefetch_related('participants', 'messages')
    
    conversations_data = []
    for conv in conversations:
        other_user = conv.participants.exclude(id=request.user.id).first()
        last_message = conv.get_last_message()
        unread_count = conv.messages.filter(is_read=False).exclude(sender=request.user).count()
        
        conversations_data.append({
            'conversation': conv,
            'other_user': other_user,
            'last_message': last_message,
            'unread_count': unread_count
        })
    
    return render(request, 'cryptix_app/conversations_list.html', {'conversations_data': conversations_data})


@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    chat_messages = conversation.messages.all().select_related('sender')
    other_user = conversation.participants.exclude(id=request.user.id).first()
    
    conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            conversation.updated_at = timezone.now()
            conversation.save()
            return redirect('conversation_detail', conversation_id=conversation.id)
    
    return render(request, 'cryptix_app/conversation_detail.html', {
        'conversation': conversation,
        'chat_messages': chat_messages,
        'other_user': other_user
    })


@login_required
def start_conversation(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    
    if other_user == request.user:
        messages.error(request, 'Ви не можете почати чат із самим собою')
        return redirect('conversations_list')
    
    existing_conversation = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    ).first()
    
    if existing_conversation:
        return redirect('conversation_detail', conversation_id=existing_conversation.id)
    
    conversation = Conversation.objects.create()
    conversation.participants.add(request.user, other_user)
    
    return redirect('conversation_detail', conversation_id=conversation.id)