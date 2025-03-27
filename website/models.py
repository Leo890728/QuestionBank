from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User
from allauth.socialaccount.signals import social_account_added, pre_social_login


@receiver(pre_social_login)
def pre_social_login_handler(sender, request, sociallogin, **kwargs):
    user = sociallogin.user

    if not UserProfile.objects.filter(user=user).exists():
        user_profile = UserProfile.objects.create(user=user, name=user.username)
        user_profile.save()
        return

    try:
        user = User.objects.get(email=user.email)
        sociallogin.connect(request, user)
    except User.DoesNotExist:
        pass 


class UserProfile(models.Model):
    user = models.OneToOneField(User, models.CASCADE, primary_key=True)
    name = models.CharField(max_length=30, blank=False)
    biography = models.CharField(max_length=200, blank=True)