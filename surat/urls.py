"""
URL configuration for surat project.

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
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", welcome, name="welcome"),
    path("detail-ketahananPangan/detail/<int:id>", detail_ketahananpangan, name="detail_ketahananpangan"),
    path("detail-pengumuman/detail/<int:id>", detail_pengumuman, name="detail_pengumuman"),
    path("detail-blog/detail/<int:id>", detail_blog, name="detail_blog"),
    path("login/", loginPage, name="loginpage"),
 
    # 
    path("dashboard/", include('dashboard.urls')),
   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)