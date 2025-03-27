from django.apps import AppConfig
from django.db.models import signals


class WebsiteConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "website"

    def ready(self):
        from avatar.models import Avatar
        from avatar.api.signals import remove_previous_avatar_images_when_update, create_default_thumbnails

        signals.pre_save.connect(
            remove_previous_avatar_images_when_update, sender=Avatar
        )
        signals.post_save.connect(create_default_thumbnails, sender=Avatar)