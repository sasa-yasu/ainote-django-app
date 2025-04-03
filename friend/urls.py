from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'friend'

urlpatterns = [
    path('', views.list_view, name='list'),
    path('list/', views.list_view, name='list'),
    path('create/', views.create_view, name='create'),
    path('delete/', views.delete_view, name='delete'),
    path('disp_qr/', views.disp_friend_qr_view, name='disp_qr'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
