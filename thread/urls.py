from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'thread'

urlpatterns = [
    path('', views.list_view, name='list'),
    path('detail/<int:pk>/', views.detail_view, name='detail'),
    path('create/', views.create_view, name='create'),
    path('update/<int:pk>/', views.update_view, name='update'),
    path('delete/<int:pk>/', views.delete_view, name='delete'),
    path('push-likes/<int:pk>/', views.push_likes, name='push_likes'),
    path('disp_qr/<int:pk>/', views.disp_qr_view, name='disp_qr'),
    path('join/', views.join_view, name='join'),
    path('leave/<int:pk>/', views.leave_view, name='leave'),
    path('chat/detail/<int:pk>/', views.chat_detail_view, name='chat_detail'),
    path('chat_create/<int:thread_pk>/', views.chat_create_view, name='chat_create'),
    path('chat_update/<int:pk>/', views.chat_update_view, name='chat_update'),
    path('chat_delete/<int:pk>/', views.chat_delete_view, name='chat_delete'),
    path('chat_push-likes/<int:pk>/', views.chat_push_likes, name='chat_push_likes'),
    path('chat_age-order-by-at/<int:pk>/', views.chat_age_order_by_at, name='chat_age_order_by_at'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
