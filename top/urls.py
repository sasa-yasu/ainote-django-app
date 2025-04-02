from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'top'

urlpatterns = [
    path('', views.Top, name='top'),
    path('signup/', views.Signup, name='signup'),
    path('login/', views.Login, name='login'),
    path('logout/', views.Logout, name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
