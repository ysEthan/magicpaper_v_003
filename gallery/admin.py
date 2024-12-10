from django.contrib import admin
from .models import Category, SPU, SKU

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'category_name_zh', 'category_name_en', 'level', 
                   'is_last_level', 'parent', 'rank_id', 'status')
    list_filter = ('level', 'is_last_level', 'status')
    search_fields = ('category_name_zh', 'category_name_en', 'description')
    ordering = ('rank_id', 'id')

@admin.register(SPU)
class SPUAdmin(admin.ModelAdmin):
    list_display = ('spu_code', 'spu_name', 'category', 'sales_channel', 
                   'status', 'created_at')
    list_filter = ('sales_channel', 'status', 'category')
    search_fields = ('spu_code', 'spu_name', 'spu_remark')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('基本信息', {
            'fields': ('spu_code', 'spu_name', 'category', 'sales_channel')
        }),
        ('其他信息', {
            'fields': ('spu_remark', 'status')
        }),
        ('系统信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(SKU)
class SKUAdmin(admin.ModelAdmin):
    list_display = ('sku_code', 'sku_name', 'spu', 'provider_name', 
                   'unit_price', 'plating_process', 'dimensions', 'status')
    list_filter = ('plating_process', 'status', 'spu')
    search_fields = ('sku_code', 'sku_name', 'provider_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('基本信息', {
            'fields': ('sku_code', 'sku_name', 'spu', 'provider_name', 'material')
        }),
        ('规格信息', {
            'fields': ('unit_price', 'weight', 'plating_process', 
                      'length', 'width', 'height', 'other_dimensions')
        }),
        ('其他信息', {
            'fields': ('img_url', 'status')
        }),
        ('系统信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
