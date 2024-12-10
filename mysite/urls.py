"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    # Django 管理后台 - 访问地址为 /admin/
    path('admin/', admin.site.urls),

    # 根路径 - 处理网站首页
    path('', include('page.urls')),

    # 各个应用的路由配置
    path('auth/', include('muggle.urls')),          # 用户认证模块
    path('gallery/', include('gallery.urls')),      # 图库模块
    path('manufacturing/', include('manufacturing.urls')), # 制造模块
    path('procurement/', include('procurement.urls')), # 采购模块
    path('storage/', include('storage.urls')),      # 存储模块
    path('trade/', include('trade.urls')),          # 交易模块
]
