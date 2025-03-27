"""
URL configuration for question_bank project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

import line_bot
import line_bot.views

import website

import question_bank.views
import website.views


urlpatterns = [
    path("", lambda request: redirect("QuizNova/index/", permanent=True)),

    path("QuizNova/", include("website.urls")),
    path("line-bot/", include("line_bot.urls")),

    path("admin/", admin.site.urls, name='admin'),

    path("category/", question_bank.views.category, name='category_list'),
    path("category/<int:category_id>/", question_bank.views.category, name='category_detail'),

    path("category/<int:category_id>/subject/", question_bank.views.subject, name='subject_list'),
    path("category/<int:category_id>/subject/<int:subject_id>/", question_bank.views.subject, name='subject_detail'),

    path("category/<int:category_id>/subject/<int:subject_id>/question/", question_bank.views.question, name='question_list'),
    path("category/<int:category_id>/subject/<int:subject_id>/question/<int:question_id>/", question_bank.views.question, name='question_detail'),

    path("category/<int:category_id>/subject/<int:subject_id>/question/<int:question_id>/option/", question_bank.views.option, name='option_list'),
    path("category/<int:category_id>/subject/<int:subject_id>/question/<int:question_id>/option/<int:option_id>/", question_bank.views.option, name='option_detail'),

    path("category/<int:category_id>/subject/<int:subject_id>/question/<int:question_id>/answer/", question_bank.views.answer, name='answer_list'),

    path("category/<int:category_id>/subject/<int:subject_id>/question/<int:question_id>/variable/", question_bank.views.variable, name='variable_list'),

]
