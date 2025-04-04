from django.urls import path
from . import views

app_name = 'mycalendar'

urlpatterns = [
    
    path('google/login/', views.google_login, name='google_login'),
    path('oauth2callback/', views.google_callback, name='google_callback'),

    path('create_event/', views.create_event_view, name='create_event'),
    path('update_event/', views.update_event_view, name='update_event'),
    path('delete_event/', views.delete_event_view, name='delete_event'),
]
