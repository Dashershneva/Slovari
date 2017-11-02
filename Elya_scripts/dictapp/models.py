#  -- coding: utf8 --
import os

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from dictapp.es.utils import add_to_index


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.user.id, filename)


class DictFile(models.Model):
    user = models.ForeignKey(User, auto_created=True)
    file = models.FileField(upload_to=user_directory_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    name = models.TextField(blank=True, null=True, max_length=600)

    def add_es(self):
        add_to_index(os.path.join(settings.MEDIA_ROOT, self.file.path))


class UserProfile(models.Model):
    user = models.OneToOneField(User)

    def __str__(self):
        return '{0} {1} ({2})'.format(self.user.first_name, self.user.last_name, self.user.username)


