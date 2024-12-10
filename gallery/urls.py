from django.shortcuts import render, redirect, HttpResponse
from django.contrib import admin
from django.urls import path, include, re_path




from . import views

app_name = 'gallery'

urlpatterns = [
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category_add'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
]
