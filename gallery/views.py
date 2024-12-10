from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from .models import Category, SPU
from .forms import CategoryForm, SPUForm
from django.core.exceptions import ValidationError
from django.db import models

class CategoryListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Category
    template_name = 'gallery/category_list.html'
    context_object_name = 'categories'
    paginate_by = 10
    permission_required = 'gallery.view_category'
    
    def handle_no_permission(self):
        messages.error(self.request, '您没有查看类目的权限')
        return redirect('home')
    
    def get_queryset(self):
        queryset = Category.objects.all()
        
        # 搜索功能
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                category_name_zh__icontains=search_query) | \
                      queryset.filter(category_name_en__icontains=search_query)
        
        # 状态筛选
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # 层级筛选
        level = self.request.GET.get('level')
        if level:
            queryset = queryset.filter(level=level)
            
        return queryset.order_by('rank_id', 'id')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_level'] = self.request.GET.get('level', '')
        return context

class CategoryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'gallery/category_form.html'
    success_url = reverse_lazy('gallery:category_list')
    permission_required = 'gallery.add_category'
    
    def handle_no_permission(self):
        messages.error(self.request, '您没有创建类目的权限')
        return redirect('gallery:category_list')
    
    def form_invalid(self, form):
        messages.error(self.request, '表单验证失败，请检查输入')
        return super().form_invalid(form)
    
    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, '类目创建成功！')
            return response
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)

class CategoryUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'gallery/category_form.html'
    success_url = reverse_lazy('gallery:category_list')
    permission_required = 'gallery.change_category'
    
    def handle_no_permission(self):
        messages.error(self.request, '您没有修改类目的权限')
        return redirect('gallery:category_list')
    
    def form_valid(self, form):
        messages.success(self.request, '类目更新成功！')
        return super().form_valid(form)

class CategoryDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Category
    template_name = 'gallery/category_confirm_delete.html'
    success_url = reverse_lazy('gallery:category_list')
    permission_required = 'gallery.delete_category'
    
    def handle_no_permission(self):
        messages.error(self.request, '您没有删除类目的权限')
        return redirect('gallery:category_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, '类目删除成功！')
        return super().delete(request, *args, **kwargs)

class SPUListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = SPU
    template_name = 'gallery/spu_list.html'
    context_object_name = 'spus'
    paginate_by = 10
    permission_required = 'gallery.view_spu'
    
    def handle_no_permission(self):
        messages.error(self.request, '您没有查看SPU的权限')
        return redirect('home')
    
    def get_queryset(self):
        queryset = SPU.objects.select_related('category').all()
        
        # 搜索功能
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                models.Q(spu_code__icontains=search_query) |
                models.Q(spu_name__icontains=search_query)
            )
        
        # 销售渠道筛选
        channel = self.request.GET.get('channel')
        if channel:
            queryset = queryset.filter(sales_channel=channel)
            
        # 类目筛选
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        # 状态筛选
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'search_query': self.request.GET.get('search', ''),
            'current_channel': self.request.GET.get('channel', ''),
            'current_category': self.request.GET.get('category', ''),
            'current_status': self.request.GET.get('status', ''),
            'categories': Category.objects.filter(is_last_level=True),
            'channel_choices': SPU.CHANNEL_CHOICES,
        })
        return context

class SPUCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = SPU
    form_class = SPUForm
    template_name = 'gallery/spu_form.html'
    success_url = reverse_lazy('gallery:spu_list')
    permission_required = 'gallery.add_spu'
    
    def handle_no_permission(self):
        messages.error(self.request, '您没有创建SPU的权限')
        return redirect('gallery:spu_list')
    
    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, 'SPU创建成功！')
            return response
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)

class SPUUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = SPU
    form_class = SPUForm
    template_name = 'gallery/spu_form.html'
    success_url = reverse_lazy('gallery:spu_list')
    permission_required = 'gallery.change_spu'
    
    def handle_no_permission(self):
        messages.error(self.request, '您没有修改SPU的权限')
        return redirect('gallery:spu_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'SPU更新成功！')
        return super().form_valid(form)

class SPUDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = SPU
    template_name = 'gallery/spu_confirm_delete.html'
    success_url = reverse_lazy('gallery:spu_list')
    permission_required = 'gallery.delete_spu'
    
    def handle_no_permission(self):
        messages.error(self.request, '您没有删除SPU的权限')
        return redirect('gallery:spu_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'SPU删除成功！')
        return super().delete(request, *args, **kwargs)
