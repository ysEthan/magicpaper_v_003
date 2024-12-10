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
    path('spus/', views.SPUListView.as_view(), name='spu_list'),
    path('spus/add/', views.SPUCreateView.as_view(), name='spu_add'),
    path('spus/<int:pk>/edit/', views.SPUUpdateView.as_view(), name='spu_edit'),
    path('spus/<int:pk>/delete/', views.SPUDeleteView.as_view(), name='spu_delete'),
    path('skus/', views.SKUListView.as_view(), name='sku_list'),
    path('skus/add/', views.SKUCreateView.as_view(), name='sku_add'),
    path('skus/<int:pk>/edit/', views.SKUUpdateView.as_view(), name='sku_edit'),
    path('skus/<int:pk>/delete/', views.SKUDeleteView.as_view(), name='sku_delete'),
    path('skus/sync/', views.SKUSyncView.as_view(), name='sku_sync'),
]
