#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.urls import path, include
from django.contrib.staticfiles import views as static_views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.decorators import login_required
import library.views as views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('register/', views.user_register, name='user_register'),
    path('set_password/', login_required(views.set_password), name='set_password'),
    path('profile/', login_required(views.profile), name='profile'),

    path('book/borrowed/', login_required(views.borrowed_books), name='borrowed_books'),
    path('book/borrow/<str:id>/<str:action>/', login_required(views.borrow), name='borrow'),

    path('static/<path:path>/', static_views.serve, name='static'),

    path('search/', views.book_search, name='book_search'),

    path('add_publisher/', login_required(views.AddPublisherView.as_view()), name='add_publisher'),
    path('add_author/', login_required(views.AddAuthorView.as_view()), name='add_author'),

    path('add_category/', login_required(views.AddCategoryView.as_view()), name='add_category'),
    path('category/<str:cats>/', views.categoryView, name='category'),
    path('categories/', views.categoriesList, name='categories_list'),

    path('about/', views.about, name='about'),

    path('create/', login_required(views.create_view), name='create'),

    path('book/detail/<str:id>/', views.book_detail, name='detail'),
    path('book/update/<str:id>/', login_required(views.update_view), name='update'),
    path('book/delete/<str:id>/', login_required(views.delete_view), name='delete'),

    path('favourite/', login_required(views.fav_view), name='favourite'),
    path('book/fav/add/<str:id>/', login_required(views.add_to_fav), name='addtofav'),
    path('book/fav/remove/<str:id>/', login_required(views.remove_fav), name='removefav'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
