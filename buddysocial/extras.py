from .models import Bookmark_Manager, Story, Profile, Notification
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

def bookmark_add_remove_manager(request, bookmark_instance):
    """This is responsible for adding stories to bookmark and removing stories from bookmark"""
    # Bookmark story
    story_to_save_id = request.POST.get("story-to-save-id")
    story_to_remove_id = request.POST.get("story-to-remove-id")

    # Handling Adding Story to Bookmark
    if story_to_save_id:
        story_to_save = Story.objects.get(id=story_to_save_id)
        bookmark_instance.story.add(story_to_save)
        bookmark_instance.save()
        # If a story is added to bookmark, update the story bookmark numbers
        story_to_save.number_of_bookmarks += 1
        story_to_save.save()
        messages.success(request, "The story has been bookmarked!")
    # Handling Removing story from Bookmark
    if story_to_remove_id:
        story_to_remove = Story.objects.get(id=story_to_remove_id)
        bookmark_instance.story.remove(story_to_remove)
        bookmark_instance.save()
        # If a story is removed from bookmark, update the story bookmark numbers
        story_to_remove.number_of_bookmarks -= 1
        story_to_remove.save()
        messages.success(request, "The story has been removed from your bookmark!")


def follow_and_unfollow_manager(request, profile):
    """This is responsible for following new users and removing existing users"""
    # Following new users
    follow_id = request.POST.get("follow-id")
    unfollow_id = request.POST.get("unfollow-id")

    # Handling Following new users
    if follow_id:
        new_user_to_follow = Profile.objects.get(id=follow_id)
        # Follow new user and save model
        profile.following.add(new_user_to_follow)
        profile.save()
        
        #Create a new notification to notify the user that gets followed
        message = f"@{profile.user.username.lower()} started following you!"
        user_to_notify_id = new_user_to_follow.user.id
        user_to_notify_instance = User.objects.get(id=user_to_notify_id) 
        Notification.objects.create(
            user=user_to_notify_instance,
            sender=new_user_to_follow,
            receiver=profile,
            message=message
        )
    # Handling removing exisiting users
    elif unfollow_id:
        new_user_to_unfollow = Profile.objects.get(id=unfollow_id)
        # Follow new user and save model
        profile.following.remove(new_user_to_unfollow)
        profile.save()
