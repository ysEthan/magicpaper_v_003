from django.shortcuts import render, redirect, HttpResponse
from django.contrib import admin
from django.urls import path, include, re_path

from . import views

urlpatterns = [
    path('', views.home_page, name='home'),

]
