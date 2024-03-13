from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.text import slugify
from shortuuid.django_fields import ShortUUIDField


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to="media/profile", null=True, blank=True)
    cover_photo = models.ImageField(upload_to="media/profile", null=True, blank=True)
    display_name = models.CharField(max_length=1000, null=True, blank=True)
    following = models.ManyToManyField(
        "self", related_name="followers", symmetrical=False, blank=True)
    bio = models.TextField(max_length=1000, null=True, blank=True)
    location = models.CharField(max_length=1000, null=True, blank=True)
    profession = models.CharField(max_length=1000, null=True, blank=True)
    date_updated = models.DateTimeField(auto_now=False, null=True, blank=True)
    date_created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user}"

class Story(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    contents = models.TextField()
    story_image = models.ImageField(
        upload_to="media/stories", null=True, blank=True)
    likes = models.IntegerField(default=0)
    number_of_comments = models.IntegerField(default=0)
    number_of_bookmarks = models.IntegerField(default=0)
    slug = ShortUUIDField(
        unique=True, length=30, max_length=35, alphabet="1234567890+=&?abcdefghijklmnopqrstuvwxyz")
    date_updated = models.DateTimeField(auto_now=False, null=True, blank=True)
    date_created = models.DateTimeField(auto_now=False)

    class Meta:
        ordering = ["-date_created"]
        verbose_name_plural = "Stories"

    def __str__(self):
        return f"{self.user.username}"


class OTP_Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    active = models.BooleanField(default=True)
    date_updated = models.DateTimeField(auto_now=False, null=True, blank=True)
    date_sent = models.DateTimeField(auto_now=True)


# class FollowUnfollowManager(models.Model):
#    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
#    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
#    following = models.ManyToManyField(Profile, related_name="following", blank=True)
#    followers = models.ManyToManyField(Profile, related_name="followers", blank=True)
#
#    def __str__(self):
#        return f"{self.user.username}"


class Bookmark_Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    story = models.ManyToManyField(Story)
    date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.user.username}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    comment = models.TextField()
    date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.user.username}"


#NOTIFICATION_TYPE = (
#    ("follow", "Follow"),
#    ("story", "Story"),
#)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="sender", blank=True, null=True)
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="receiver", blank=True, null=True)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.user.username}"


# class BookmarkCategory(models.Model):
#    user = models.ForeignKey(User, on_delete=models.CASCADE)
#    category_title = models.CharField(max_length=500)
#    cate_slug = models.SlugField(
#        blank=False, null=False, default="", db_index=True, max_length=500)
#
#    def save(self, **args):
#        self.cate_slug = slugify(self.category_title)
#        super().save(**args)
#
#    def __str__(self):
#        return self.category_title

# class Bookmark(models.Model):
#    user = models.ForeignKey(User, on_delete=models.CASCADE)
#    story = models.ManyToManyField(Story)
#    category = models.OneToOneField(BookmarkCategory, on_delete=models.CASCADE)
#    date = models.DateTimeField(auto_now=True)
#
#    class Meta:
#        ordering = ["-date"]
#
#    def __str__(self):
#        return f"{self.user.username}"
