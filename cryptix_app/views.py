from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.contrib import messages
from django.utils import timezone
from .forms import RegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import Friendship, Follow, Conversation, Message, Group, GroupMembership, GroupPost, GroupPostComment, Profile


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
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Профіль оновлено!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)
    
    return render(request, 'cryptix_app/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


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


@login_required
def groups_list(request):
    all_groups = Group.objects.all().prefetch_related('members')
    my_groups = request.user.joined_groups.all()
    
    return render(request, 'cryptix_app/groups_list.html', {
        'all_groups': all_groups,
        'my_groups': my_groups
    })


@login_required
def group_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        is_private = request.POST.get('is_private') == 'on'
        avatar = request.FILES.get('avatar')
        
        group = Group.objects.create(
            name=name,
            description=description,
            is_private=is_private,
            avatar=avatar,
            creator=request.user
        )
        
        GroupMembership.objects.create(
            user=request.user,
            group=group,
            role='admin'
        )
        
        messages.success(request, f'Група "{name}" створена!')
        return redirect('group_detail', group_id=group.id)
    
    return render(request, 'cryptix_app/group_create.html')


@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    is_member = group.members.filter(id=request.user.id).exists()
    
    if group.is_private and not is_member:
        messages.error(request, 'Це приватна група')
        return redirect('groups_list')
    
    posts = group.posts.all().select_related('author').prefetch_related('comments')
    membership = None
    
    if is_member:
        membership = GroupMembership.objects.get(user=request.user, group=group)
    
    # -- створення постів
    if request.method == 'POST' and is_member:
        if 'post_content' in request.POST:
            content = request.POST.get('post_content', '').strip()
            image = request.FILES.get('post_image')
            if content:
                GroupPost.objects.create(
                    group=group,
                    author=request.user,
                    content=content,
                    image=image
                )
                messages.success(request, 'Пост створено!')
                return redirect('group_detail', group_id=group.id)
    
    return render(request, 'cryptix_app/group_detail.html', {
        'group': group,
        'posts': posts,
        'is_member': is_member,
        'membership': membership
    })


@login_required
def group_join(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    
    if group.is_private:
        messages.error(request, 'Неможливо приєднатися до приватної групи')
        return redirect('groups_list')
    
    GroupMembership.objects.get_or_create(
        user=request.user,
        group=group,
        defaults={'role': 'member'}
    )
    
    messages.success(request, f'Ви приєдналися до групи "{group.name}"')
    return redirect('group_detail', group_id=group.id)


@login_required
def group_leave(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    
    if group.creator == request.user:
        messages.error(request, 'Створювач не може покинути групу')
        return redirect('group_detail', group_id=group.id)
    
    GroupMembership.objects.filter(user=request.user, group=group).delete()
    messages.success(request, f'Ви покинули групу "{group.name}"')
    return redirect('groups_list')


@login_required
def group_post_comment(request, post_id):
    post = get_object_or_404(GroupPost, id=post_id)
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            GroupPostComment.objects.create(
                post=post,
                author=request.user,
                content=content
            )
            messages.success(request, 'Коментар додано!')
    
    return redirect('group_detail', group_id=post.group.id)


@login_required
def group_delete(request, group_id):
    group = get_object_or_404(Group, id=group_id, creator=request.user)
    group.delete()
    messages.success(request, 'Групу видалено')
    return redirect('groups_list')


# -- профілі

@login_required
def user_profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile, created = Profile.objects.get_or_create(user=profile_user)
    
    is_friend = False
    friendship_status = None
    is_following = False
    
    if request.user != profile_user:
        friendship = Friendship.objects.filter(
            Q(from_user=request.user, to_user=profile_user) |
            Q(from_user=profile_user, to_user=request.user)
        ).first()
        
        if friendship:
            if friendship.status == 'accepted':
                is_friend = True
            else:
                friendship_status = friendship.status
        
        is_following = Follow.objects.filter(
            follower=request.user,
            following=profile_user
        ).exists()
    
    friends_count = Friendship.objects.filter(
        Q(from_user=profile_user, status='accepted') |
        Q(to_user=profile_user, status='accepted')
    ).count()
    
    followers_count = Follow.objects.filter(following=profile_user).count()
    following_count = Follow.objects.filter(follower=profile_user).count()
    groups_count = profile_user.joined_groups.count()
    
    return render(request, 'cryptix_app/user_profile.html', {
        'profile_user': profile_user,
        'profile': profile,
        'is_friend': is_friend,
        'friendship_status': friendship_status,
        'is_following': is_following,
        'friends_count': friends_count,
        'followers_count': followers_count,
        'following_count': following_count,
        'groups_count': groups_count,
    })