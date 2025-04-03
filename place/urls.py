from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'place'

urlpatterns = [
    path('', views.list_view, name='list'),
    path('list/', views.list_view, name='list'),
    path('detail/<int:pk>/', views.detail_view, name='detail'),
    path('create/', views.create_view, name='create'),
    path('update/<int:pk>/', views.update_view, name='update'),
    path('delete/<int:pk>/', views.delete_view, name='delete'),
    path('push-likes/<int:pk>/', views.push_likes, name='push_likes'),
    path('disp_in_qr/', views.disp_checkin_qr_view, name='disp_in_qr'),
    path('checkin/', views.checkin_view, name='checkin'),
    path('disp_out_qr/', views.disp_checkout_qr_view, name='disp_out_qr'),
    path('checkout/', views.checkout_view, name='checkout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
