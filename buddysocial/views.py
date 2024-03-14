from django.shortcuts import render, redirect
from .forms import SignUpForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import update_session_auth_hash
from .models import Profile, OTP_Manager, Story, Bookmark_Manager, Comment, Notification
from .verification_mail import (
    verification_email,
    OTP_Expiration_Manager,
    Resend_OTP_Manager,
)
from . import forgot_password_mail
from django.contrib.auth.models import User
from .extras import bookmark_add_remove_manager, follow_and_unfollow_manager
from datetime import datetime
from django.db.models import Q


# Onboarding Page
def onboarding_view(request):
    # Checking if user is authenticated
    user = request.user
    if user.is_authenticated:
        return redirect("home")
    return render(request, "buddysocial/index.html")


# Signup Page
def signup_view(request):
    # Checking if user is authenticated
    user = request.user
    if user.is_authenticated:
        return redirect("home")

    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password2"]

            # Save to database
            form.save(commit=True)

            # Send verification mail to user
            verification_email(request, email, username)

            # Create user profile
            user_instance = User.objects.get(username=username)
            Profile.objects.create(user=user_instance)

            # Login Users
            user = authenticate(request, username=username, password=password)
            login(request, user)

            return redirect("verify-account")

    return render(request, "buddysocial/signup.html", {"signup_form": form})


# Login Page
def login_view(request):
    # Checking if user is authenticated
    user = request.user
    if user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        all_users = User.objects.all()
        all_users_usernames = [user.username for user in all_users]
        try:
            user = authenticate(request, username=username, password=password)
            login(request, user)
            messages.success(request, "Login successful, Welcome Back!")
            return redirect("home")
        except:
            if username not in all_users_usernames:
                messages.error(
                    request, "This username does not exist, create an account instead!"
                )
            else:
                messages.error(request, "Your password is incorrect!")
    return render(request, "buddysocial/login.html")


@login_required
def logout_user(request):
    logout(request)
    return redirect("onboarding")


# Verify Account
def verify_account(request):

    OTP_Expiration_Manager(request)

    username = request.user.username
    user_instance = User.objects.get(username=username)
    try:
        saved_otp = OTP_Manager.objects.get(user=user_instance)
    except:
        saved_otp = ""
    if request.method == "POST":
        inserted_otp = request.POST.get("otp")
        if inserted_otp:
            otp = saved_otp.otp
            otp_status = saved_otp.active
            if otp_status:
                if inserted_otp == otp:
                    return redirect("verify-success")
                else:
                    messages.error(
                        request,
                        "The OTP you just inserted is incorrect! Please check your mail and try again",
                    )
            else:
                messages.error(
                    request, "Your OTP is expired, please request for a new OTP!"
                )
        else:
            Resend_OTP_Manager(request)
            messages.success(request, "A new OTP has been sent to your email address")

    return render(request, "buddysocial/verify_account.html")


# Reset Password
def reset_password1(request):
    # Checking if user is authenticated
    user = request.user
    if user.is_authenticated:
        return redirect("home")
    
    if request.method == "POST":
        username = request.POST.get("username")
        #To check if username exists in the database
        all_users = User.objects.all()
        all_usernames = [user.username for user in all_users]
        if username in all_usernames:
            user_instance = User.objects.get(username=username)
            receiver_address = user_instance.email
            #Send user verification mail
            forgot_password_mail.verification_email(request, receiver_address, username)
            return redirect("reset-password2", username)
        else:
            messages.success(request, "This username doesn't exists in our records")
            return redirect("reset-password1")
    return render(request, "buddysocial/reset_password1.html")


def reset_password2(request, username):
    user_instance = User.objects.get(username=username)

    forgot_password_mail.OTP_Expiration_Manager(request, user_instance)

    # Checking if user is authenticated
    user = request.user
    if user.is_authenticated:
        return redirect("home")

    try:
        saved_otp = OTP_Manager.objects.get(user=user_instance)
    except:
        saved_otp = ""

    if request.method == "POST":
        inserted_otp = request.POST.get("otp")
        if inserted_otp:
            otp = saved_otp.otp
            otp_status = saved_otp.active
            print(otp_status)
            if otp_status:
                if inserted_otp == otp:
                    return redirect("reset-password3", username)
                else:
                    messages.error(
                        request,
                        "The OTP you just inserted is incorrect! Please check your mail and try again",
                    )
            else:
                messages.error(
                    request, "Your OTP is expired, please request for a new OTP!"
                )
        else:
            forgot_password_mail.Resend_OTP_Manager(request, username)
            messages.success(request, "A new OTP has been sent to your email address")

    return render(request, "buddysocial/reset_password2.html")


def reset_password3(request, username):
    # Checking if user is authenticated
    user = request.user
    if user.is_authenticated:
        return redirect("home")
    
    if request.method == "POST":
        password = request.POST.get("password1")
        confirm_password = request.POST.get("password2")
        if password == confirm_password:
            user_instance = User.objects.get(username=username) 
            # Hashed the password and save it to the database
            hashed_password = make_password(confirm_password)
            user_instance.password = hashed_password
            user_instance.save()
            # Update the session with the user's current password
            update_session_auth_hash(request, user_instance)
            messages.success(
                    request, "Your password reset is successful"
            )
            return redirect("login")
        else:
            messages.error(request, "The both fields must match")

    return render(request, "buddysocial/reset_password3.html")


# Verification Success
def verify_success(request):
    return render(request, "buddysocial/verify_success.html")


# Home page
@login_required
def home_view(request):
    user = request.user
    user_instance = User.objects.get(id=user.id)

    try:
        bookmark_instance = Bookmark_Manager.objects.get(user=user_instance)
        # All Bookmarked stories
        all_bookmarks = bookmark_instance.story.all()
        all_bookmarks_id = [story.id for story in all_bookmarks]
    except:
        bookmark_instance = Bookmark_Manager.objects.create(user=user_instance)
        all_bookmarks = []
        all_bookmarks_id = []
    try:
        profile = Profile.objects.get(user=user_instance)
    except:
        profile = None

    # Who to follow
    all_profiles = Profile.objects.all().exclude(user=user_instance)
    # All users following
    try:
        all_following = profile.following.all()
        who_to_follow = [user for user in all_profiles if user not in all_following]
    except:
        who_to_follow = []

    # Made for you stories (All stories) and Following stories
    try:
        all_stories = Story.objects.all()
        # To access the stories written by authors that the user is following
        following_stories = [
            story for story in all_stories if story.profile in all_following
        ]
    except:
        all_stories = None
        following_stories = None

    if request.method == "POST":
        story_contents = request.POST.get("new-story")
        story_picture = request.FILES.get("story-cover-image")

        # Like Story
        # story_slug = request.POST.get("storyslug")

        # Bookmark_Manager story
        story_to_save_id = request.POST.get("story-to-save-id")
        story_to_remove_id = request.POST.get("story-to-remove-id")

        # Following new users
        profile_id = request.POST.get("follow-id")

        # Handling Writing Story
        if story_contents:
            date = datetime.now()
            new_story = Story.objects.create(
                user=user_instance,
                profile=profile,
                contents=story_contents,
                date_created=date,
            )
            # If user uploaded a image save it to the story model
            if story_picture is not None:
                new_story.story_image = story_picture
                new_story.save()
            #Create a new notification when a user create a new story
            message = "Your story has been posted successfully!"
            Notification.objects.create(
                user=user_instance,
                sender=profile,
                receiver=profile,
                story=new_story,
                message=message
            )
            messages.success(request, "Your story has been posted successfully!")
            return redirect("home")

        # Handling following users
        elif profile_id:
            new_user_to_follow = Profile.objects.get(id=profile_id)
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
            return redirect("home")

        # Handling Adding Story to Bookmark_Manager
        elif story_to_save_id:
            story_to_save = Story.objects.get(id=story_to_save_id)
            bookmark_instance.story.add(story_to_save)
            bookmark_instance.save()

            # If a story is added to bookmark, update the story bookmark numbers
            story_to_save.number_of_bookmarks += 1
            story_to_save.save()

            messages.success(request, "The story has been bookmarked!")
            return redirect("home")
        # Handling Removing story from Bookmark_Manager
        elif story_to_remove_id:
            story_to_remove = Story.objects.get(id=story_to_remove_id)
            bookmark_instance.story.remove(story_to_remove)
            bookmark_instance.save()

            # If a story is removed from bookmark, update the story bookmark numbers
            story_to_remove.number_of_bookmarks -= 1
            story_to_remove.save()

            messages.success(request, "The story has been removed from your bookmark!")
            return redirect("home")

    return render(
        request,
        "buddysocial/home.html",
        {
            "profile": profile,
            "made_for_you_stories": all_stories,
            "who_to_follow": who_to_follow,
            "all_bookmarks_id": all_bookmarks_id,
            "following_stories": following_stories,
        },
    )


# View Story
def view_story(request, username, slug):
    # Show story
    user = request.user
    try:
        user_instance = User.objects.get(id=user.id)
        profile = Profile.objects.get(user=user_instance)
    except:
        user_instance = None
        profile = None

    story = Story.objects.get(slug=slug)

    # Bookmark_Manager story
    try:
        bookmark_instance = Bookmark_Manager.objects.get(user=user_instance)
        # All Bookmarked stories
        all_bookmarks = bookmark_instance.story.all()
        all_bookmarks_id = [story.id for story in all_bookmarks]
    except:
        bookmark_instance = Bookmark_Manager.objects.create(user=user_instance)
        all_bookmarks = []
        all_bookmarks_id = []

    # All comments
    comments = Comment.objects.filter(story=story).all()

    # Who to follow
    all_profiles = Profile.objects.all().exclude(user=user_instance)
    # All users following
    try:
        all_following = profile.following.all()
        who_to_follow = [user for user in all_profiles if user not in all_following]
    except:
        who_to_follow = []

    # Latest From Author
    stories_from_author = (
        Story.objects.filter(user__username=username)
        .exclude(id=story.id)
        .order_by("-date_created")[:3]
    )

    #Accepts POST requests only when users is logged in
    if user.is_authenticated:
        if request.method == "POST":
            comment_content = request.POST.get("comment-content")
            author_to_follow_id = request.POST.get("author-to-follow")
            author_to_unfollow_id = request.POST.get("author-to-unfollow")

            # Following new users
            profile_id = request.POST.get("follow-id")

            # Bookmark_Manager

            story_to_save_id = request.POST.get("story-to-save-id")
            story_to_remove_id = request.POST.get("story-to-remove-id")

            # Handling Adding Story to Bookmark_Manager
            if story_to_save_id:
                story_to_save = Story.objects.get(id=story_to_save_id)
                bookmark_instance.story.add(story_to_save)

                # If a story is added to bookmark, update the story bookmark numbers
                story_to_save.number_of_bookmarks += 1
                story_to_save.save()

                bookmark_instance.save()

                messages.success(request, "The story has been bookmarked!")
                return redirect("view-story", username=username, slug=slug)
            # Handling Removing story from Bookmark_Manager
            if story_to_remove_id:
                story_to_remove = Story.objects.get(id=story_to_remove_id)
                bookmark_instance.story.remove(story_to_remove)

                # If a story is removed from bookmark, update the story bookmark numbers
                story_to_remove.number_of_bookmarks -= 1
                story_to_remove.save()

                bookmark_instance.save()

                messages.success(request, "The story has been removed from your bookmark!")
                return redirect("view-story", username=username, slug=slug)

            # Handling Writing Comments
            if comment_content:
                # Create new comment
                Comment.objects.create(
                    user=user_instance,
                    profile=profile,
                    story=story,
                    comment=comment_content,
                )
                # If a comment is added to story, update the story comment numbers
                story.number_of_comments += 1
                story.save()

                # Create a new notification to notify the user which story has a new comment
                message = f"@{profile.user.username.lower()} commented on your story"
                user_to_notify_id = story.user.id
                user_to_notify_instance = User.objects.get(id=user_to_notify_id)
                user_to_notify_profile = Profile.objects.get(user=user_to_notify_instance)
                Notification.objects.create(
                    user=user_to_notify_instance,
                    sender=user_to_notify_profile,
                    receiver=profile,
                    story=story,
                    message=message,
                )
                messages.success(request, "Your comment has been posted successfully!")
                return redirect("view-story", username=username, slug=slug)
            # Handling Following story author
            if author_to_follow_id:
                new_user_to_follow = Profile.objects.get(id=author_to_follow_id)
                # Follow new user and save model
                profile.following.add(new_user_to_follow)
                profile.save()

                # Create a new notification to notify the user that gets followed
                message = f"@{profile.user.username.lower()} started following you!"
                user_to_notify_id = new_user_to_follow.user.id
                user_to_notify_instance = User.objects.get(id=user_to_notify_id)
                Notification.objects.create(
                    user=user_to_notify_instance,
                    sender=new_user_to_follow,
                    receiver=profile,
                    message=message,
                )
                return redirect("view-story", username, slug)
            # Handling Unfollowing story author
            elif author_to_unfollow_id:
                new_user_to_unfollow = Profile.objects.get(id=author_to_unfollow_id)
                # Follow new user and save model
                profile.following.remove(new_user_to_unfollow)
                profile.save()
                return redirect("view-story", username, slug)
            # Handling Following new users
            elif profile_id:
                new_user_to_follow = Profile.objects.get(id=profile_id)
                # Follow new user and save model
                profile.following.add(new_user_to_follow)
                profile.save()

                # Create a new notification to notify the user that gets followed
                message = f"@{profile.user.username.lower()} started following you!"
                user_to_notify_id = new_user_to_follow.user.id
                user_to_notify_instance = User.objects.get(id=user_to_notify_id)
                Notification.objects.create(
                    user=user_to_notify_instance,
                    sender=new_user_to_follow,
                    receiver=profile,
                    message=message,
                )
                return redirect("view-story", username, slug)
    else:
        messages.error(request, "Please login to use that feature!")
    return render(
        request,
        "buddysocial/view_story.html",
        {
            "story": story,
            "comments": comments,
            "who_to_follow": who_to_follow,
            "stories_from_author": stories_from_author,
            "all_bookmarks_id": all_bookmarks_id,
            "profile": profile,
        },
    )


# Write story
@login_required
def write_story(request):
    user = request.user
    user_instance = User.objects.get(id=user.id)
    try:
        profile = Profile.objects.get(user=user_instance)
    except:
        profile = None

    # Handling Writing Story
    if request.method == "POST":
        story_contents = request.POST.get("new-story")
        story_picture = request.FILES.get("story-cover-image")
        if story_contents:
            date = datetime.now()
            new_story = Story.objects.create(
                user=user_instance,
                profile=profile,
                contents=story_contents,
                date_created=date,
            )
            # If user uploaded a image save it to the story model
            if story_picture is not None:
                new_story.story_image = story_picture
                new_story.save()
            messages.success(request, "Your story has been posted successfully!")
            return redirect("home")
    return render(request, "buddysocial/write_story.html", {"profile": profile})


# Bookmark_Manager
@login_required
def bookmark_view(request):
    user = request.user
    user_instance = User.objects.get(id=user.id)
    profile = Profile.objects.get(user=user_instance)
    bookmark_instance = Bookmark_Manager.objects.get(user=user_instance)

    # Bookmark_Manager story
    try:
        bookmark_instance = Bookmark_Manager.objects.get(user=user_instance)
        # All Bookmarked stories
        all_bookmarks = bookmark_instance.story.all()
        all_bookmarks_id = [story.id for story in all_bookmarks]
    except:
        bookmark_instance = Bookmark_Manager.objects.create(user=user_instance)
        all_bookmarks = []
        all_bookmarks_id = []

    # Who to follow
    all_profiles = Profile.objects.all().exclude(user=user_instance)
    # All users following
    try:
        all_following = profile.following.all()
        who_to_follow = [user for user in all_profiles if user not in all_following]
    except:
        who_to_follow = []

    if request.method == "POST":

        # Following new users
        profile_id = request.POST.get("follow-id")
        # Bookmark to remove
        story_to_remove_id = request.POST.get("story-to-remove-id")

        # Handling Following new users
        if profile_id:
            new_user_to_follow = Profile.objects.get(id=profile_id)
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
            return redirect("bookmark")

        # Bookmark add and remove
        # Handling Removing story from Bookmark_Manager
        if story_to_remove_id:
            story_to_remove = Story.objects.get(id=story_to_remove_id)
            bookmark_instance.story.remove(story_to_remove)

            # If a story is removed from bookmark, update the story bookmark numbers
            story_to_remove.number_of_bookmarks -= 1
            story_to_remove.save()

            bookmark_instance.save()

            messages.success(request, "The story has been removed from your bookmark!")
            return redirect("bookmark")

    return render(
        request,
        "buddysocial/bookmark_open.html",
        {
            "who_to_follow": who_to_follow,
            "all_bookmarks": all_bookmarks,
            "all_bookmarks_id": all_bookmarks_id,
            "profile": profile,
        },
    )


## Bookmark_Manager Open
# def bookmark_open_view(request, bm_slug):
#    return render(request, "buddysocial/bookmark_open.html")


# Profile
@login_required
def profile(request, username):
    user = request.user
    user_instance = User.objects.get(username=username)
    # To check who is viewing this profile section, if it is not the user instance, it will redirect to the others profile
    if user.id == user_instance.id:
        # Profile
        profile = Profile.objects.get(user=user_instance)

        # All Stories
        all_stories = Story.objects.filter(user=user_instance).order_by("-date_created")

        # Bookmark_Manager story
        try:
            bookmark_instance = Bookmark_Manager.objects.get(user=user_instance)
            # All Bookmarked stories
            all_bookmarks = bookmark_instance.story.all()
            all_bookmarks_id = [story.id for story in all_bookmarks]
        except:
            bookmark_instance = Bookmark_Manager.objects.create(user=user_instance)
            all_bookmarks = []
            all_bookmarks_id = []

        # Who to follow
        all_profiles = Profile.objects.all().exclude(user=user_instance)
        # All users following
        try:
            all_following = profile.following.all()
            who_to_follow = [user for user in all_profiles if user not in all_following]
        except:
            who_to_follow = []

        if request.method == "POST":
            story_to_delete_id = request.POST.get("story-to-delete-id")

            # Following new users
            profile_id = request.POST.get("follow-id")

            # Adding story to bookmark and removing story from bookmark
            bookmark_add_remove_manager(request, bookmark_instance)

            # Deleting story
            if story_to_delete_id:
                story_to_delete = Story.objects.get(id=story_to_delete_id)
                story_to_delete.delete()
                messages.success(request, "Your story has been deleted successfully")

            # Handling Following new users
            if profile_id:
                new_user_to_follow = Profile.objects.get(id=profile_id)
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
            return redirect("profile", username)
    else:
        u_name = user_instance.username
        return redirect("other-users-profile", u_name)
    return render(
        request,
        "buddysocial/profile.html",
        {
            "profile": profile,
            "all_stories": all_stories,
            "all_bookmarks_id": all_bookmarks_id,
            "who_to_follow": who_to_follow,
        },
    )


# User Following
@login_required
def user_following(request):
    user = request.user
    user_instance = User.objects.get(id=user.id)

    # Profile
    profile = Profile.objects.get(user=user_instance)

    all_following = profile.following.all()

    if request.method == "POST":
        # Unfollowing users
        follow_and_unfollow_manager(request, profile)
        return redirect("user-following")

    return render(
        request,
        "buddysocial/user_following.html",
        {
            "all_following": all_following,
            "profile": profile,
        },
    )


# User Followers
@login_required
def user_followers(request):
    user = request.user
    user_instance = User.objects.get(id=user.id)
    # Profile
    profile = Profile.objects.get(user=user_instance)

    # All Followers
    all_followers = profile.followers.all()
    all_following = profile.following.all()
    all_following_id = [user.id for user in all_following]

    if request.method == "POST":
        # Following and Unfollowing users
        follow_and_unfollow_manager(request, profile)
        return redirect("user-followers")

    return render(
        request,
        "buddysocial/user_follower.html",
        {
            "profile": profile,
            "all_followers": all_followers,
            "all_following_id": all_following_id,
        },
    )


# Edit Profile
@login_required
def edit_profile(request):
    user = request.user
    user_instance = User.objects.get(id=user.id)
    # Profile
    profile = Profile.objects.get(user=user_instance)

    # Updating profile
    if request.method == "POST":
        new_cover_photo = request.FILES.get("new-cover-photo")
        new_profile_picture = request.FILES.get("new-profile-picture")
        new_display_name = request.POST.get("profile-display-name")
        new_bio = request.POST.get("new-bio")
        new_location = request.POST.get("new-location")
        new_profession = request.POST.get("new-profession")

        # Updating user profile with the details above
        if new_cover_photo:
            profile.cover_photo = new_cover_photo
        elif new_profile_picture:
            profile.profile_picture = new_profile_picture
        profile.display_name = new_display_name
        profile.bio = new_bio
        profile.location = new_location
        profile.profession = new_profession
        profile.save()
        messages.success(request, "Your profile has been updated successfully!")
        return redirect("profile", user_instance.username)
    return render(request, "buddysocial/edit_profile.html", {"profile": profile})


# Other Users Profile
def other_users_profile(request, username):
    user_instance = User.objects.get(username=username)
    user = request.user
    loggin_user_username = user.username

    # All Stories
    all_stories = Story.objects.filter(user=user_instance)

    # Checking if user is logged in user, if true redirect to the user profile instead
    if user.id == user_instance.id:
        return redirect("profile", loggin_user_username)
    else:
        # Profile
        profile = Profile.objects.get(user=user_instance)
        # All following
        try:
            loggedin_user_instance = User.objects.get(id=user.id)
            loggedin_user_profile = Profile.objects.get(user=loggedin_user_instance)
            all_following = loggedin_user_profile.following.all()
        except:
            loggedin_user_instance = None
            loggedin_user_profile = None
            all_following = []

        all_following_id = [user.id for user in all_following]

        # Bookmark_Manager story
        try:
            bookmark_instance = Bookmark_Manager.objects.get(
                user=loggedin_user_instance
            )
            # All Bookmarked stories
            all_bookmarks = bookmark_instance.story.all()
            all_bookmarks_id = [story.id for story in all_bookmarks]
        except:
            bookmark_instance = Bookmark_Manager.objects.create(
                user=loggedin_user_instance
            )
            all_bookmarks = []
            all_bookmarks_id = []

        # Who to follow
        all_profiles = Profile.objects.all().exclude(user=loggedin_user_instance)
        # All users following
        try:
            all_following = loggedin_user_profile.following.all()
            who_to_follow = [user for user in all_profiles if user not in all_following]
        except:
            who_to_follow = []

        # Only accept POST requests for authenticated users, if not authenticated redirect to the login page
        if request.method == "POST":
            if user.is_authenticated:
                # Following new users
                follow_and_unfollow_manager(request, profile=loggedin_user_profile)
                # Adding story to bookmark and removing story from bookmark
                bookmark_add_remove_manager(request, bookmark_instance)
                return redirect("other-users-profile", username)
            else:
                return redirect("login")
    return render(
        request,
        "buddysocial/profile_others.html",
        {
            "profile": loggedin_user_profile,
            "author_profile": profile,
            "all_following_id": all_following_id,
            "all_stories": all_stories,
            "all_bookmarks_id": all_bookmarks_id,
            "who_to_follow": who_to_follow,
        },
    )


# Settings
@login_required
def settings_view(request):
    user = request.user
    user_instance = User.objects.get(id=user.id)
    profile = Profile.objects.get(user=user_instance)
    if request.method == "POST":
        old_password = request.POST.get("old-password")
        new_password = request.POST.get("new-password1")
        confirm_password = request.POST.get("new-password2")
        saved_password = user_instance.password
        # To check if the inserted password is valid compared to what is saved on the database.
        password_check = check_password(old_password, saved_password)
        if password_check:
            # Check if the new_password field and confirm password field matches before updating the password
            if new_password == confirm_password:
                # Hashed the password and save it to the database
                hashed_password = make_password(confirm_password)
                user_instance.password = hashed_password
                user_instance.save()
                # Update the session with the user's current password
                update_session_auth_hash(request, user)
                messages.success(
                    request, "Your password has been updated successfully!"
                )
                return redirect("profile", user_instance.username)
            else:
                messages.error(
                    request, "The new password and confirm password fields must match"
                )
        else:
            messages.error(
                request,
                "Your current password is incorrect, please check and try again!",
            )
    return render(request, "buddysocial/settings.html", {"profile": profile})


# Notifications
@login_required
def notifications_view(request):
    user = request.user
    user_instance = User.objects.get(id=user.id)
    profile = Profile.objects.get(user=user_instance)
    all_notifications = Notification.objects.filter(user=user_instance).order_by("-date")
    return render(request, "buddysocial/notification.html", {
        "profile": profile,
        "all_notifications": all_notifications
    })

# Search
@login_required
def search_view(request):
    user = request.user
    user_instance = User.objects.get(id=user.id)
    profile = Profile.objects.get(user=user_instance)
    all_stories_for_search = []
    all_users_for_search = []
    search_query = ""

    # For Search Results
    search_query = request.GET.get("query")
    if search_query:
        try:
            # Search results for stories
            all_stories_for_search = Story.objects.filter(
                Q(contents__icontains=search_query)
            )

            # Search results for users
            all_users_for_search = Profile.objects.filter(
                Q(user__username__icontains=search_query)
            )
        except:
            all_stories_for_search = []
            all_users_for_search = []

    # Bookmark_Manager story
    try:
        bookmark_instance = Bookmark_Manager.objects.get(user=user_instance)
        # All Bookmarked stories
        all_bookmarks = bookmark_instance.story.all()
        all_bookmarks_id = [story.id for story in all_bookmarks]
    except:
        bookmark_instance = Bookmark_Manager.objects.create(user=user_instance)
        all_bookmarks = []
        all_bookmarks_id = []

    # Who to follow
    all_profiles = Profile.objects.all().exclude(user=user_instance)
    # All users following
    try:
        all_following = profile.following.all()
        who_to_follow = [user for user in all_profiles if user not in all_following]
        all_following_id = [user.id for user in all_following]
    except:
        who_to_follow = []
        all_following_id = []

    # POST Requests
    if request.method == "POST":
        # Adding story to bookmark and removing story from bookmark
        bookmark_add_remove_manager(request, bookmark_instance)
        # Following new users
        follow_and_unfollow_manager(request, profile=profile)
        return redirect("search")

    return render(
        request,
        "buddysocial/search.html",
        {
            "profile": profile,
            "all_stories_for_search": all_stories_for_search,
            "all_bookmarks_id": all_bookmarks_id,
            "all_users_for_search": all_users_for_search,
            "all_following_id": all_following_id,
            "who_to_follow": who_to_follow,
            "loggedin_user": user_instance,
            "search_query": search_query,
        },
    )
