from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_signin, logout as auth_signout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from allauth.socialaccount.models import SocialAccount

from website.forms import RegisterForm, LoginForm, ProfileEditForm
from website.models import UserProfile
from question_bank.database import QuestionBank

# Create your views here.

def get_accounts_info(request) -> dict[str, SocialAccount | User]:
    user = None
    user_profile = None
    google_account = None
    line_account = None
    if request.user.is_authenticated:
        user = request.user
        user_profile = UserProfile.objects.filter(user=user).first()
        if (social_accounts := SocialAccount.objects.filter(user=user)).exists():
            google_account = social_accounts.filter(user=user, provider='google').first()
            line_account = social_accounts.filter(user=user, provider='line').first()
    return {
        "user": user,
        "user_profile": user_profile,
        "google_account": google_account,
        "line_account": line_account
    }
        

def index(request):
    
    context = {
        "is_authenticated": request.user.is_authenticated,
        **get_accounts_info(request),
    }

    return render(request, 'index.html', context=context)

@login_required
@csrf_exempt
def profile(request):
    context = {
        "is_authenticated": True,
        **get_accounts_info(request),
    }
    match request.method:
        
        case "GET":
            form = ProfileEditForm()

        case "POST":
            form = ProfileEditForm(request.POST)
            if form.is_valid():
                user_profile = context["user_profile"]
                user_profile.name = form.cleaned_data["name"]
                user_profile.biography = form.cleaned_data["biography"]
                user_profile.save()
                messages.success(request, "修改成功!")
                form = ProfileEditForm()
            else:
                messages.error(request, "修改失敗")

    context.setdefault("user_profile_form", form)
    return render(request, "profile.html", context=context)

@csrf_exempt
def signin_signup(request):
    if request.user.is_authenticated:
        return redirect("profile")
    
    match request.method:
        case "GET":
            context = {
                "signup_form": RegisterForm(),
                "signin_form": LoginForm(),
            }

        case "POST":
            if (action := request.POST.get("action")) == "signin":
                return signin(request)
            elif action == "signup":
                return signup(request)
            else:
                return redirect("signin-signup")

    return render(request, "signin-signup.html", context=context)


def signup(request) -> HttpResponse:
    form = RegisterForm(request.POST)
    if form.is_valid():
        user = form.save()
        name = form.data["username"]
        UserProfile.objects.create(user=user, name=name)
        messages.success(request, "註冊成功！請登入您的帳戶。", extra_tags="signup")
        return redirect("signin-signup")
    else:
        context = {
            "signup_form": form,
            "signin_form": LoginForm(),
            "status": "signup"
        }
        messages.error(request, "註冊失敗!", extra_tags="signup")
    return render(request, "signin-signup.html", context=context)


def signin(request) -> HttpResponse:
    form = LoginForm(request.POST)

    context = {
        "signup_form": RegisterForm(),
        "signin_form": form,
        "status": "signin"
    }

    if not form.is_valid():
        messages.error(request, "輸入的帳戶名稱或密碼格式有誤！", extra_tags="signin")
        return render(request, "signin-signup.html", context=context)

    username = form.cleaned_data["username"]
    password = form.cleaned_data["password"]

    user = authenticate(request, username=username, password=password)

    if user is not None:
        auth_signin(request, user)
        return redirect("index")
    else:
        messages.error(request, "帳戶名稱或密碼錯誤!", extra_tags="signin")
        
        return render(request, "signin-signup.html", context=context)

@login_required
@csrf_exempt
def categorys(request):
    return render(request, "categorys.html")
