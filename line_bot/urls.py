from django.contrib import admin
from django.urls import include, path

import line_bot.views

urlpatterns = [
    path("", line_bot.views.callback, name='line_bot_callback'),
]