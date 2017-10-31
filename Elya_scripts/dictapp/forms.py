# -*- coding: utf-8 -*-

from django import forms
from dictapp.models import DictFile


class UserCreationForm(forms.Form):
    username = forms.CharField()
    email = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField()
    last_name = forms.CharField()


class UserProfileForm(forms.Form):
    first_name = forms.CharField(label='Имя', required=True)
    last_name = forms.CharField(label='Фамилия', required=True)
    new_password = forms.CharField(label='Новый пароль', widget=forms.PasswordInput,
        help_text="Заполните, чтобы поменять пароль, или оставьте поле пустым", required=False)
    new_password_repeated = forms.CharField(label='Новый пароль ещё раз', widget=forms.PasswordInput, required=False)


class DictFileForm(forms.ModelForm):
    class Meta:
        model = DictFile
        fields = ('file', 'user')