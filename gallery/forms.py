from django import forms
from django.core.exceptions import ValidationError
from .models import Category, SPU, SKU

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name_zh', 'category_name_en', 'description', 
                 'image', 'parent', 'rank_id', 'level', 'status']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 添加 Bootstrap 类
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        
        # 根据选择的层级过滤可选的父类目
        self.fields['parent'].queryset = Category.objects.all()
        
        # 添加帮助文本
        self.fields['level'].help_text = '请先选择层级，然后选择对应的父类目'
        self.fields['parent'].help_text = '父类目的层级必须小于当前类目的层级'

    def clean(self):
        cleaned_data = super().clean()
        parent = cleaned_data.get('parent')
        level = cleaned_data.get('level')

        if level is None:
            raise ValidationError('请选择层级')

        # 验证父类目和层级的关系
        if parent:
            if level <= parent.level:
                raise ValidationError({
                    'level': '子类目的层级必须大于父类目的层级',
                    'parent': '父类目的层级必须小于当前类目的层级'
                })
        elif level != 1:
            raise ValidationError({
                'level': '没有父类目时，必须是一级分类',
                'parent': '非一级分类必须选择父类目'
            })

        return cleaned_data

class SPUForm(forms.ModelForm):
    class Meta:
        model = SPU
        fields = ['spu_code', 'spu_name', 'spu_remark', 'sales_channel', 
                 'category', 'status']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 添加 Bootstrap 类
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        
        # 只显示最后一级类目
        self.fields['category'].queryset = Category.objects.filter(is_last_level=True)
        
        # 添加帮助文本
        self.fields['spu_code'].help_text = '唯一的SPU标识码，至少4个字符'
        self.fields['category'].help_text = '只能选择最后一级类目'

class SKUForm(forms.ModelForm):
    # 重新定义状态字段
    status = forms.BooleanField(
        required=False,  # 允许为空
        initial=True,    # 默认为True
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'checked': 'checked'  # 确保默认选中
        })
    )

    class Meta:
        model = SKU
        fields = ['sku_code', 'sku_name', 'provider_name', 'unit_price', 
                 'weight', 'plating_process', 'length', 'width', 'height', 
                 'other_dimensions', 'material', 'color', 'img_url', 'spu', 'status']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 添加空选项到电镀工艺选择
        self.fields['plating_process'].choices = [('', '请选择电镀工艺')] + list(self.fields['plating_process'].choices)[1:]
        
        # 添加 Bootstrap 类和 placeholder，必填项添加 *
        field_labels = {
            'sku_code': 'SKU编码 (至少4个字符) *',
            'sku_name': 'SKU名称 *',
            'provider_name': '供应商',  # 非必填
            'unit_price': '单价 (元)',  # 非必填
            'length': '长度 (mm)',  # 非必填
            'width': '宽度 (mm)',   # 非必填
            'height': '高度 (mm)',  # 非必填
            'weight': '重量 (kg)',  # 非必填
            'other_dimensions': '其他尺寸',  # 非必填
            'plating_process': '请选择电镀工艺',  # 非必填
            'material': '材质',  # 非必填
            'color': '颜色',  # 非必填
            'img_url': '产品图片'  # 非必填
        }
        
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name in field_labels:
                field.widget.attrs['placeholder'] = field_labels[field_name]
                field.label = ''  # 移除标签
                
                # 特殊处理需要空初始值的字段
                if field_name in ['provider_name', 'length', 'width', 'height', 'unit_price', 'weight', 'plating_process', 'material', 'color']:
                    field.initial = ''  # 设置初始值为空
                    
                # 特殊处理电镀工艺下拉框
                if field_name == 'plating_process':
                    field.widget.attrs.update({
                        'class': 'form-select form-select-sm',  # 使用 Bootstrap 的 select 样式
                    })
        
        # 只显示启用状态的SPU
        self.fields['spu'].queryset = SPU.objects.filter(status=True)
        
        # 确保状态默认为启用
        self.fields['status'].initial = True