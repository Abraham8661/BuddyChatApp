from django.db import models
from django.contrib.auth.models import User
from buddysocial.models import Profile
from shortuuid.django_fields import ShortUUIDField

class ChatRoom(models.Model):
    sender_user = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="sender_user")
    receiver_user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="receiver_user")
    sender_user_profile = models.ForeignKey(Profile, on_delete=models.DO_NOTHING, related_name="sender_user_profile", null=True)
    receiver_user_profile = models.ForeignKey(
        Profile, on_delete=models.DO_NOTHING, related_name="receiver_user_profile", null=True)
    slug = ShortUUIDField(
        unique=True, length=30, max_length=35, alphabet="1234567890+=&?abcdefghijklmnopqrstuvwxyz")
    date = models.DateTimeField(auto_now=True)

class Chat(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="sender")
    receiver = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="receiver")
    sender_profile = models.ForeignKey(Profile, on_delete=models.DO_NOTHING, related_name="sender_profile")
    receiver_profile = models.ForeignKey(
        Profile, on_delete=models.DO_NOTHING, related_name="receiver_profile")
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, null=True)
    message = models.TextField()
    updated = models.DateTimeField(auto_now=False, null=True, blank=True)
    date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"{self.sender.username} message to {self.receiver.username}"


#
# class ChatManager(models.Model):
#
#     user = models.OneToOneField(User, on_delete=models.DO_NOTHING)
#
#     chat = models.ManyToManyField(Chat)
#
#     room = models.ManyToManyField(ChatRoom)
#
#     date = models.DateTimeField(auto_now=True)
#

#
#     class Meta:
#
#         ordering = ["date"]
