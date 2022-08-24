

from django.urls import path, re_path
from app import views
from . import views_dash,views_dash2,views_dash3

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    # The home page
    

    path('', views.index, name='home'),
    path('result/', views_dash.result, name='result'),
    path('result2/', views_dash2.result2, name='result2'),
    path('result3/', views_dash3.result3, name='result3'),




    
    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),
    

]

if settings.DEBUG:
    urlpatterns += static (settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

