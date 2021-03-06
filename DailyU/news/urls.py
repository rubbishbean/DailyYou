from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views


from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/', views.login,name='login'),
    url(r'^logout/', views.logout,name='logout'),
    url(r'^posts/$',views.newspaperIndex,name='sections'),
    url(r'^posts/(?P<section_name>[\w\-]+)/$',views.generateNewspaper,name='posts'),
    url(r'^archive/$',views.newspaper_archive,name='archive'),
    url(r'^save/$',views.html_to_pdf_directly,name='save'),
    url(r'^archive/pdfs/(?P<pdf_name>[\w\-]+)/$',views.view_pdf,name='view_pdf'),
    url(r'^editcat/', views.editCategory, name='editcat')
]