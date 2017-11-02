"""vd URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.views import login, logout
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static

from dictapp.views.pages import index, about, help
from dictapp.views.profile import profile, register_user, model_form_upload, handle_uploads

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', index, name='index'),
    url(r'^about/$', about, name='about'),
    url(r'^help/', help, name='help'),

    url(r'^accounts/register/$', register_user, name='register'),
    url(r'^accounts/login/$', login, {'template_name': 'login.html'}, name='login'),
    url(r'^accounts/logout/$', logout, {'next_page': settings.LOGIN_REDIRECT_URL}, name='logout'),
    url(r'^accounts/', include('password_reset.urls')),

    url(r'^profile/([^/]+)/$', profile, name="profile"),
    url(r'^profile/([^/]+)/upload$', model_form_upload, name="upload"),
    url(r'^profile/([^/]+)/files$', handle_uploads, name="handle_uploads"),
    ]


if settings.DEBUG:
    urlpatterns += static(r'media/', document_root=settings.MEDIA_ROOT)