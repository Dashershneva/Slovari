#  -- coding: utf8 --

from django.contrib import admin

from dictapp.models import *


# class TokenAdmin(admin.ModelAdmin):
#     list_display = ('text', 'text_eng', 'text_rus', 'created')  # в таблице

admin.site.register(UserProfile)
admin.site.register(DictFile)