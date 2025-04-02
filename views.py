from django.shortcuts import render

def custom_404_view(request, exception):
    """ 404 エラーページ表示 """
    return render(request, '404.html', status=404)
