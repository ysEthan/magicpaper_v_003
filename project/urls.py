from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('muggle.urls')),  # 包含 muggle 应用的 URLs
] 