"""
URL configuration for AinoteProject project.

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
from top.views import Top

urlpatterns = [
    path('admin/', admin.site.urls),
    path('maintenance-mode/', include('maintenance_mode.urls')),
 
    path('', Top, name='top'),
 
    path('top/', include('top.urls')),
    path('notice/', include('notice.urls')),
    path('headline/', include('headline.urls')),
    path('group/', include('group.urls')),
    path('user/', include('user.urls')),
    path('findme/', include('findme.urls')),
    path('friend/', include('friend.urls')),
    path('chat/', include('chat.urls')),
    path('thread/', include('thread.urls')),
    path('mycalendar/', include('mycalendar.urls')),
    path('room/', include('room.urls')),
    path('device/', include('device.urls')),
    path('place/', include('place.urls')),
    path('sharedfile/', include('sharedfile.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)