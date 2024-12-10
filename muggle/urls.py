from django.shortcuts import render, redirect, HttpResponse
from django.contrib import admin
from django.urls import path, include, re_path




from . import views

app_name = 'muggle'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('password/change/', views.change_password_view, name='change_password'),
]
