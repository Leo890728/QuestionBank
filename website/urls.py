from django.urls import include, path
from django.contrib.auth.views import LogoutView

import website.views

urlpatterns = [
    path("index/", website.views.index, name="index"),
    path("profile/", website.views.profile, name="profile"),
    path("signin-signup/", website.views.signin_signup, name="signin-signup"),
    path('signout/', LogoutView.as_view(), name="signout"),
    path("categorys/", website.views.categorys, name="categorys"),
    
    path("social-login/", include("allauth.urls")),
    path('avatar/', include('avatar.urls')),
    path('api/', include('avatar.api.urls'), name="avatar-api"),
]