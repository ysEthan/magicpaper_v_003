from django.shortcuts import render, HttpResponse, redirect


def home_page(request):
    return render(request, "home_page.html")
