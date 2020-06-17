
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from . import views, search, search2

urlpatterns = [
    path('runoob/', views.runoob),
    url(r'^search-form$', search.search_form),
    url(r'^search$', search.search),
    url(r'^search-post$', search2.search_post),

]
