from django.urls import path
from . import views
from chat.views import chat_view, open_chat_view

urlpatterns = [
    path("", views.onboarding_view, name="onboarding"),
    path("accounts/signup", views.signup_view, name="signup"),
    path("accounts/login/", views.login_view, name="login"),
    path("accounts/logout", views.logout_user, name="logout"),
    path("accounts/verify-account", views.verify_account, name="verify-account"),
    path("accounts/reset-password1", views.reset_password1, name="reset-password1"),
    path("accounts/reset-password2/<username>", views.reset_password2, name="reset-password2"),
    path("accounts/reset-password3/<username>", views.reset_password3, name="reset-password3"),
    path("accounts/verify-success", views.verify_success, name="verify-success"),
    path("home", views.home_view, name="home"),
    path("story/@<username>/<slug>", views.view_story, name="view-story"),
    path("write-story", views.write_story, name="write-story"),
    # Chat
    path("chat", chat_view, name="chat"),
    path("chat/@<username>/<slug>", open_chat_view, name="open-chat"),
    # Bookmark
    path("bookmark", views.bookmark_view, name="bookmark"),
    # path("bookmark/<slug:bm_slug>", views.bookmark_open_view, name="bookmark-open"),
    # Profile
    path("profile/@<username>", views.profile, name="profile"),
    # Other Users Profile
    path("users/profile/@<username>", views.other_users_profile, name="other-users-profile"),
    # Edit Profile
    path("profile/edit-profile", views.edit_profile, name="edit-profile"),
    # Setting
    path("account/settings", views.settings_view, name="setting"),
    # User Following
    path("profile/following", views.user_following, name="user-following"),
    # User Followers
    path("profile/followers", views.user_followers, name="user-followers"),
    # Notifications
    path("notifications", views.notifications_view, name="notifications"),
    # Search
    path("search", views.search_view, name="search"),
]
