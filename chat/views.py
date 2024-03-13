from django.shortcuts import render, redirect
from .models import Chat, Profile, ChatRoom
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.decorators import login_required

# Create your views here.


# Chat section
@login_required
def chat_view(request):
    user = request.user
    user_instance = User.objects.get(id=user.id)
    all_chats = ChatRoom.objects.filter(
        Q(sender_user=user_instance) | Q(receiver_user=user_instance)
    ).order_by("-date")

    # All followers and Following of user
    profile = Profile.objects.get(user=user_instance)
    all_following = profile.following.all()
    all_followers = profile.followers.all()
    all_chat_profiles = [profile.sender_user_profile for profile in all_chats]
    all_chat_profiles2 = [profile.receiver_user_profile for profile in all_chats]
    all_chat_profile_list = [profile for profile in all_chat_profiles and all_chat_profiles2]
    all_buddies = []
    for user in all_following:
        if user not in all_chat_profile_list:
            all_buddies.append(user)
    for user in all_followers:
        if user not in all_chat_profile_list:
            all_buddies.append(user)

    ## Accessing buddy to chat with
    ##Create chatroom for all Buddies
    if request.method == "POST":
        # chat_room = None
        receiver_user_id = request.POST.get("receiver-user-id")
        receiver_user_instance = User.objects.get(id=receiver_user_id)
        receiver_user_profile = Profile.objects.get(user=receiver_user_instance)
        sender_user_profile = Profile.objects.get(user=user_instance)

        # Create new chat room
        chat_room = ChatRoom.objects.create(
            sender_user = user_instance,
            sender_user_profile = sender_user_profile,
            receiver_user = receiver_user_instance,
            receiver_user_profile = receiver_user_profile
        )

        # Redirect to the chat page
        return redirect("open-chat", receiver_user_instance.username, chat_room.slug)
    return render(
        request,
        "buddysocial/chat.html",
        {
            "all_chats": all_chats,
            "all_buddies": all_buddies,
            "profile": profile
        },
    )


# Open story
@login_required
def open_chat_view(request, username, slug):
    user = request.user
    user_instance = User.objects.get(id=user.id)
    profile = Profile.objects.get(user=user_instance)

    chat_room = ChatRoom.objects.get(slug=slug)
    chats = Chat.objects.filter(room=chat_room)
    recent_message = chats.last()
    receiver = Profile.objects.get(user__username=username)
    return render(
        request,
        "buddysocial/open-chat.html",
        {
            "chat_room": chat_room,
            "receiver": receiver,
            "chats": chats,
            "recent_message": recent_message,
            "profile": profile,
        },
    )
