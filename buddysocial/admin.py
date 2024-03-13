from django.contrib import admin
from .models import Profile, Story, Comment, Notification, OTP_Manager


admin.site.register(Profile)
admin.site.register(Story)
admin.site.register(Comment)
admin.site.register(Notification)
admin.site.register(OTP_Manager)