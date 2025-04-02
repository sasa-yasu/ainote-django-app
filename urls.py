from django.conf.urls import handler404
from . import views

# 404エラーをカスタムページに設定
handler404 = 'AinoteProject.views.custom_404_view'
