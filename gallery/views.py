from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from .models import Category, SPU, SKU
from .forms import CategoryForm, SPUForm, SKUForm
from django.core.exceptions import ValidationError
from django.db import models
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
from django.views import View
from .sync import ProductSync
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404

class CategoryListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Category
    template_name = 'gallery/category/category_list.html'
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
    template_name = 'gallery/category/category_form.html'
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
    template_name = 'gallery/category/category_form.html'
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
    template_name = 'gallery/category/category_confirm_delete.html'
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
    template_name = 'gallery/spu/spu_list.html'
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
    template_name = 'gallery/spu/spu_form.html'
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
    template_name = 'gallery/spu/spu_form.html'
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
    template_name = 'gallery/spu/spu_confirm_delete.html'
    success_url = reverse_lazy('gallery:spu_list')
    permission_required = 'gallery.delete_spu'
    
    def handle_no_permission(self):
        messages.error(self.request, '您没有删除SPU的权限')
        return redirect('gallery:spu_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'SPU删除成功！')
        return super().delete(request, *args, **kwargs)

class SKUListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = SKU
    template_name = 'gallery/sku/sku_list.html'
    context_object_name = 'skus'
    paginate_by = 10
    permission_required = 'gallery.view_sku'
    
    def handle_no_permission(self):
        messages.error(self.request, '您没有查看SKU的权限')
        return redirect('home')
    
    def get_queryset(self):
        # 使用 select_related 预加载 spu 和 category 数据
        queryset = SKU.objects.select_related(
            'spu',
            'spu__category'  # 预加载 SPU 的类目数据
        ).all()
        
        # 搜索功能
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                models.Q(sku_code__icontains=search_query) |
                models.Q(sku_name__icontains=search_query) |
                models.Q(provider_name__icontains=search_query) |
                models.Q(spu__category__category_name_zh__icontains=search_query)  # 添加类目搜索
            )
        
        # SPU筛选
        spu_id = self.request.GET.get('spu')
        if spu_id:
            queryset = queryset.filter(spu_id=spu_id)
            
        # 类目筛选
        category_id = self.request.GET.get('category')  # 添加类目筛选
        if category_id:
            queryset = queryset.filter(spu__category_id=category_id)
            
        # 电镀工艺筛选
        plating = self.request.GET.get('plating')
        if plating:
            queryset = queryset.filter(plating_process=plating)
            
        # 状态筛选
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # 供应商筛选
        provider = self.request.GET.get('provider')
        if provider:
            queryset = queryset.filter(provider_name=provider)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 获取所有供应商名称（去重）
        providers = SKU.objects.exclude(
            provider_name=''
        ).values_list(
            'provider_name', flat=True
        ).distinct().order_by('provider_name')
        
        # 获取所有启用状态的SPU（按名称去重）
        spus = SPU.objects.filter(
            status=True
        ).values('spu_name').annotate(
            first_id=models.Min('id'),
            first_code=models.Min('spu_code')
        ).values(
            'first_id',
            'spu_name',
            'first_code'
        ).order_by('spu_name')
        
        # 转换SPU数据格式
        spus = [
            {
                'id': spu['first_id'],
                'spu_name': spu['spu_name'],
                'spu_code': spu['first_code']
            }
            for spu in spus
        ]
        
        # 获取所有电镀工艺（去重）
        plating_processes = SKU.objects.exclude(
            plating_process=''
        ).values_list(
            'plating_process', flat=True
        ).distinct()
        
        # 获取所有SPU名称和对应的电镀工艺
        spu_plating = SKU.objects.exclude(
            plating_process=''
        ).values_list(
            'spu__spu_name', 'plating_process'
        ).distinct()
        
        # 按SPU分组电镀工艺
        spu_plating_dict = {}
        for spu_name, plating in spu_plating:
            if spu_name not in spu_plating_dict:
                spu_plating_dict[spu_name] = set()
            spu_plating_dict[spu_name].add(plating)
        
        # 构建电镀工艺选项（按SPU分组后去重）
        all_plating_processes = set()
        for plating_set in spu_plating_dict.values():
            all_plating_processes.update(plating_set)
        
        plating_choices = [
            (process, dict(SKU.PLATING_PROCESS_CHOICES).get(process, process))
            for process in sorted(all_plating_processes)
        ]
        
        # 获取所有在用的类目（通过SKU关联的SPU）
        categories = Category.objects.filter(
            spus__skus__isnull=False  # 只获取有SKU关联的类目
        ).distinct().values(
            'id',
            'category_name_zh',
            'category_name_en',
            'parent__category_name_zh'  # 获取父类目名称
        ).order_by(
            'parent__category_name_zh',
            'category_name_zh'
        )
        
        # 构建类目显示名称（包含父类目）
        categories_list = [
            {
                'id': cat['id'],
                'name': f"{cat['parent__category_name_zh']} > {cat['category_name_zh']}" if cat['parent__category_name_zh'] else cat['category_name_zh']
            }
            for cat in categories
        ]
        
        context.update({
            'search_query': self.request.GET.get('search', ''),
            'current_spu': self.request.GET.get('spu', ''),
            'current_plating': self.request.GET.get('plating', ''),
            'current_status': self.request.GET.get('status', ''),
            'current_provider': self.request.GET.get('provider', ''),
            'current_category': self.request.GET.get('category', ''),
            'spus': spus,
            'plating_choices': plating_choices,
            'providers': providers,
            'categories': categories_list,  # 使用新的类目列表
        })
        return context

class SKUCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = SKU
    form_class = SKUForm
    template_name = 'gallery/sku/sku_form.html'
    success_url = reverse_lazy('gallery:sku_list')
    permission_required = 'gallery.add_sku'
    
    def handle_no_permission(self):
        messages.error(self.request, '您没有创建SKU的权限')
        return redirect('gallery:sku_list')
    
    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, 'SKU创建成功！')
            return response
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)

class SKUUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = SKU
    form_class = SKUForm
    template_name = 'gallery/sku/sku_form.html'
    success_url = reverse_lazy('gallery:sku_list')
    permission_required = 'gallery.change_sku'
    
    def handle_no_permission(self):
        messages.error(self.request, '您没有修改SKU的权限')
        return redirect('gallery:sku_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'SKU更新成功！')
        return super().form_valid(form)

class SKUDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = SKU
    template_name = 'gallery/sku/sku_confirm_delete.html'
    success_url = reverse_lazy('gallery:sku_list')
    permission_required = 'gallery.delete_sku'
    
    def handle_no_permission(self):
        messages.error(self.request, '您没有删除SKU的权限')
        return redirect('gallery:sku_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'SKU删除成功！')
        return super().delete(request, *args, **kwargs)

@method_decorator([require_POST, permission_required('gallery.sync_sku', raise_exception=True)], name='dispatch')
class SKUSyncView(View):
    def post(self, request, *args, **kwargs):
        print("\n=== 开始同步数据 ===")
        print(f"请求方法: {request.method}")
        print(f"Content-Type: {request.headers.get('Content-Type')}")
        print(f"用户: {request.user}")
        print(f"权限: {request.user.has_perm('gallery.sync_sku')}")
        
        try:
            sync = ProductSync()
            print("创建 ProductSync 实例成功")
            
            synced_count = sync.sync_products()
            print(f"同步完成，共同步 {synced_count} 条数据")
            
            response_data = {
                'success': True,
                'message': f'成功同步 {synced_count} 条数据'
            }
            print("返回数据:", response_data)
            return JsonResponse(response_data)
            
        except Exception as e:
            print(f"同步失败: {str(e)}")
            print(f"错误类型: {type(e)}")
            import traceback
            print("错误堆栈:", traceback.format_exc())
            
            return JsonResponse({
                'success': False,
                'message': str(e)
            })

@require_http_methods(["GET"])
def spu_detail_api(request, pk):
    spu = get_object_or_404(SPU, pk=pk)
    return JsonResponse({
        'spu_code': spu.spu_code,
        'spu_name': spu.spu_name,
        'category_name': spu.category.full_name,
        'sales_channel_display': spu.get_sales_channel_display(),
        'spu_remark': spu.spu_remark,
    })

@require_http_methods(["GET"])
def spu_search_api(request):
    query = request.GET.get('term', '')
    spus = SPU.objects.filter(
        models.Q(spu_code__icontains=query) |
        models.Q(spu_name__icontains=query)
    ).filter(
        status=True
    ).only(
        'id', 'spu_code', 'spu_name'
    )[:10]  # 限制返回数量
    
    results = [{'id': spu.id, 'text': f"{spu.spu_code} - {spu.spu_name}"} for spu in spus]
    return JsonResponse({'results': results})
