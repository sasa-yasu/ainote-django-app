from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'sharedfile'

urlpatterns = [
    path('', views.list_view, name='list'),
    path('detail/<int:pk>/', views.detail_view, name='detail'),
    path('create/', views.create_view, name='create'),
    path('update/<int:pk>/', views.update_view, name='update'),
    path('delete/<int:pk>/', views.delete_view, name='delete'),
    path('push-likes/<int:pk>/', views.push_likes, name='push_likes'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
