from django import forms
from django.core.exceptions import ValidationError
from .models import Category

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