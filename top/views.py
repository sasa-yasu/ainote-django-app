from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from headline.models import Headline
from notice.models import Notice

# Create your views here.
def Top(request):
    headline_object_list = Headline.objects.order_by('published_at').all()
    notice_object_list = Notice.objects.order_by('published_at').all()
    top_calendar_monthly = f'{settings.TOP_CALENDAR_MONTHLY}'
    top_calendar_weekly = f'{settings.TOP_CALENDAR_WEEKLY}'

    context = {
        'headline_object_list': headline_object_list, 'notice_object_list': notice_object_list,
        'top_calendar_monthly': top_calendar_monthly, 'top_calendar_weekly': top_calendar_weekly
    }
    return render(request, 'top/index.html', context)


def Signup(request):
    if request.method == "POST":
        username_data = request.POST["username"]
        password_data = request.POST["password"]
        password_verify_data = request.POST["password_verify"]
        if password_data == password_verify_data:
            try:
                User.objects.create_user(username_data, '', password_data)
            except IntegrityError:
                return render(request, 'user/signup.html', {'error': 'このユーザーは既に登録されています'})
            return redirect('top:login')
        else:
            return render(request, 'user/signup.html', {'error': '入力されたパスワードが不一致です'})

    else:
        return render(request, 'top/signup.html')


def Login(request):
    if request.method == "POST":
        username_data = request.POST["username"]
        password_data = request.POST["password"]
        next_data = request.POST["next"]
        user = authenticate(request, username=username_data, password=password_data)
        if user is not None:
            login(request, user)

            if next_data:
                return redirect(next_data)
            else:
                return redirect('top:top')
        else:
            return redirect('top:login')
    return render(request, 'top/login.html')


def Logout(request):
    logout(request)
    return redirect('top:top')

