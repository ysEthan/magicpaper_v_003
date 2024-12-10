from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
import uuid
import os

def category_image_path(instance, filename):
    # 获取文件扩展名
    ext = filename.split('.')[-1]
    # 使用 UUID 生成唯一文件名
    if instance.pk:
        new_filename = f"category_{instance.pk}_{instance.category_name_en}.{ext}"
    else:
        new_filename = f"category_{uuid.uuid4().hex[:8]}_{instance.category_name_en}.{ext}"
    return os.path.join('categories', new_filename)

class Category(models.Model):
    STATUS_CHOICES = (
        (1, '启用'),
        (0, '禁用'),
    )
    
    LEVEL_CHOICES = (
        (1, '一级分类'),
        (2, '二级分类'),
        (3, '三级分类'),
    )

    id = models.AutoField(primary_key=True, verbose_name='分类ID')
    category_name_en = models.CharField(max_length=100, verbose_name='英文名称')
    category_name_zh = models.CharField(max_length=100, verbose_name='中文名称')
    description = models.TextField(blank=True, null=True, verbose_name='分类描述')
    image = models.ImageField(
        upload_to=category_image_path, 
        blank=True, 
        null=True, 
        verbose_name='分类图片'
    )
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children',
        verbose_name='父分类'
    )
    rank_id = models.IntegerField(default=0, verbose_name='排序ID')
    original_data = models.JSONField(
        null=True, 
        blank=True, 
        verbose_name='原始数据'
    )
    level = models.IntegerField(
        choices=LEVEL_CHOICES,
        default=1,
        verbose_name='分类层级'
    )
    is_last_level = models.BooleanField(
        default=False, 
        verbose_name='是否最后一级'
    )
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=1,
        verbose_name='状态'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'gallery_category'
        verbose_name = '分类'
        verbose_name_plural = '分类'
        ordering = ['rank_id', 'id']

    def __str__(self):
        return f"{self.category_name_zh} ({self.category_name_en})"

    def clean(self):
        # 验证父类目和层级的关系
        if self.parent:
            if self.level <= self.parent.level:
                raise ValidationError('子类目的层级必须大于父类目的层级')
        elif self.level != 1:
            raise ValidationError('没有父类目时，必须是一级分类')

    def save(self, *args, **kwargs):
        self.clean()
        # 保存记录
        super().save(*args, **kwargs)
        
        # 如果有图片且文件名不包含正确的ID，则重命名
        if self.image and not self.image.name.startswith(f'categories/category_{self.pk}_'):
            # 获取原始文件名和扩展名
            old_path = self.image.path
            filename = os.path.basename(self.image.name)
            ext = filename.split('.')[-1]
            
            # 生成新的文件名
            new_filename = f"category_{self.pk}_{self.category_name_en}.{ext}"
            new_path = os.path.join('categories', new_filename)
            
            # 更新图片字段
            self.image.name = new_path
            # 再次保存以更新数据库中的文件名
            super().save(update_fields=['image'])
            
            # 如果旧文件存在，则重命名文件
            if os.path.exists(old_path):
                new_full_path = os.path.join(settings.MEDIA_ROOT, new_path)
                os.makedirs(os.path.dirname(new_full_path), exist_ok=True)
                os.rename(old_path, new_full_path)

    @property
    def full_name(self):
        """返回完整的分类路径名称"""
        if self.parent:
            return f"{self.parent.full_name} > {self.category_name_zh}"
        return self.category_name_zh
