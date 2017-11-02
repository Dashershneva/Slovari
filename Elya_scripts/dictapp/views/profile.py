from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, HttpResponse
from dictapp.forms import DictFileForm

from dictapp.forms import UserCreationForm
from dictapp.models import UserProfile, DictFile
from dictapp.views.validate import validate_it

import os

def register_callback(user):
    user_profile = UserProfile(user=user)
    user_profile.save()


def profile(request, username):
    user = User.objects.get(username=username)
    return render(request, 'profile.html', locals())


def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            if User.objects.filter(username=username):
                error = 'Пользователь с таким логином уже существует'
                return render(request, 'register.html', locals())

            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']

            user = User.objects.create_user(username, email, password=password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            user_profile = UserProfile(user=user)
            user_profile.save()

            user = authenticate(username=username, password=password)
            login(request, user)

            return redirect(request.GET.get('next', '/') or '/')

    form = UserCreationForm()
    next_page = request.GET.get('next', '/')
    return render(request, 'register.html', locals())


def model_form_upload(request, user):
    if request.method == 'POST':
        form = DictFileForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = DictFile(file=request.FILES['file'], user=request.user)
            newdoc.save()
            valid, error, name = validate_it(os.path.join(settings.MEDIA_ROOT, newdoc.file.path))
            if not valid:
                newdoc.delete()
            else:
                newdoc.name = name
                newdoc.save()
            show_form = True if not valid else False
            return render(request, 'dict_upload.html', {'form': form, 'show_form':show_form, 'valid':valid, 'error': error})
        else:
            render(request, 'dict_upload.html', {'form': form, 'show_form':True, 'valid':True})
    else:
        form = DictFileForm()
    return render(request, 'dict_upload.html', {'form': form, 'show_form':True, 'valid':True})


def handle_uploads(request, user):
    if request.method == 'POST':
        values = request.POST.getlist('files[]')
        action = request.POST['action']
        if action == 'delete':
            for i in values:
                DictFile.objects.get(pk=int(i)).delete()
        else:
            for i in values:
                DictFile.objects.get(pk=int(i)).add_es()
    files = DictFile.objects.filter(user=request.user)
    return render(request, 'user_files.html', {'files': files})