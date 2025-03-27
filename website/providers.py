from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount
from avatar.utils import get_primary_avatar
from avatar.conf import settings as avatar_settings


class GoogleAvatarProvider:
    @classmethod
    def get_avatar_url(cls, user: User, width: int=65, height: int=65) -> str | None:
        if (google_account := SocialAccount.objects.filter(user=user, provider='google')).exists():
            if avatar_url := google_account[0].get_avatar_url():
                parameter_position = avatar_url.rfind("=")
                return avatar_url[:parameter_position+1] + f"s{max(width, height)}-c"

        return None


class LineAvatarProvider:

    @classmethod
    def get_avatar_url(cls, user: User, width: int=51, height_: int|None=None) -> str | None:
        if (line_account := SocialAccount.objects.filter(user=user, provider='line')).exists():
            if avatar_url := line_account[0].get_avatar_url():
                size = min(200, max(51, width)) # large 200x200, smail 51x51
                return f"{avatar_url}/{'small' if size == 51 else 'large'}"
            
        return None