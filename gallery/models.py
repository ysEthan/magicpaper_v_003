from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
import uuid
import os
from django.core.validators import MinValueValidator

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

class SPU(models.Model):
    CHANNEL_CHOICES = (
        (1, '线上'),
        (2, '线下'),
        (3, '全渠道'),
    )

    id = models.AutoField(primary_key=True, verbose_name='SPU ID')
    spu_code = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name='SPU编码',
        help_text='唯一的SPU标识码'
    )
    spu_name = models.CharField(
        max_length=200, 
        verbose_name='SPU名称',
        help_text='产品名称'
    )
    spu_remark = models.TextField(
        blank=True, 
        null=True, 
        verbose_name='备注',
        help_text='产品描述或其他备注信息'
    )
    sales_channel = models.IntegerField(
        choices=CHANNEL_CHOICES,
        default=3,
        verbose_name='销售渠道',
        help_text='产品销售渠道'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,  # 防止删除仍有SPU的类目
        related_name='spus',
        verbose_name='所属类目',
        help_text='产品所属类目'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name='更新时间'
    )
    status = models.BooleanField(
        default=True,
        verbose_name='状态',
        help_text='是否启用'
    )

    class Meta:
        db_table = 'gallery_spu'
        verbose_name = 'SPU'
        verbose_name_plural = 'SPU列表'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['spu_code']),
            models.Index(fields=['category']),
            models.Index(fields=['sales_channel']),
        ]

    def __str__(self):
        return f"{self.spu_code} - {self.spu_name}"

    def clean(self):
        # 验证SPU编码格式
        if self.spu_code:
            # 可以添加自定义的编码格式验证
            if len(self.spu_code) < 4:
                raise ValidationError({
                    'spu_code': 'SPU编码长度不能小于4个字符'
                })
        
        # 验证类目是否是最后一级
        if self.category and not self.category.is_last_level:
            raise ValidationError({
                'category': '只能选择最后一级类目'
            })

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def channel_display(self):
        """返回销售渠道的显示名称"""
        return self.get_sales_channel_display()

    @property
    def category_full_name(self):
        """返回完整的类目路径"""
        return self.category.full_name if self.category else ''

class SKU(models.Model):
    PLATING_PROCESS_CHOICES = (
        ('none', '无电镀'),
        ('gold', '镀金'),
        ('silver', '镀银'),
        ('nickel', '镀镍'),
        ('chrome', '镀铬'),
        ('copper', '镀铜'),
        ('other', '其他'),
    )

    id = models.AutoField(primary_key=True, verbose_name='SKU ID')
    sku_code = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name='SKU编码',
        help_text='唯一的SKU标识码'
    )
    sku_name = models.CharField(
        max_length=200, 
        verbose_name='SKU名称',
        help_text='产品具体型号名称'
    )
    provider_name = models.CharField(
        max_length=100,
        verbose_name='供应商名称',
        help_text='产品供应商'
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='单价',
        help_text='产品单价（元）'
    )
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(0)],
        verbose_name='重量',
        help_text='产品重量（kg）'
    )
    plating_process = models.CharField(
        max_length=20,
        choices=PLATING_PROCESS_CHOICES,
        default='none',
        verbose_name='电镀工艺',
        help_text='产品电镀工艺'
    )
    length = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='长度',
        help_text='产品长度（mm）'
    )
    width = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='宽度',
        help_text='产品宽度（mm）'
    )
    height = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='高度',
        help_text='产品高度（mm）'
    )
    other_dimensions = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='其他尺寸',
        help_text='其他尺寸规格描述'
    )
    material = models.CharField(
        max_length=100,
        verbose_name='材质',
        help_text='产品材质'
    )
    img_url = models.ImageField(
        upload_to='skus',
        blank=True,
        null=True,
        verbose_name='产品图片',
        help_text='产品图片'
    )
    spu = models.ForeignKey(
        'SPU',
        on_delete=models.CASCADE,
        related_name='skus',
        verbose_name='所属SPU',
        help_text='产品所属SPU'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name='更新时间'
    )
    status = models.BooleanField(
        default=True,
        verbose_name='状态',
        help_text='是否启用'
    )

    class Meta:
        db_table = 'gallery_sku'
        verbose_name = 'SKU'
        verbose_name_plural = 'SKU列表'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sku_code']),
            models.Index(fields=['spu']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.sku_code} - {self.sku_name}"

    def clean(self):
        # 验证SKU编码格式
        if self.sku_code:
            if len(self.sku_code) < 4:
                raise ValidationError({
                    'sku_code': 'SKU编码长度不能小于4个字符'
                })

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        """返回完整的SKU名称"""
        return f"{self.spu.spu_name} - {self.sku_name}"

    @property
    def dimensions(self):
        """返回标准尺寸描述"""
        return f"{self.length}*{self.width}*{self.height}mm"

    @property
    def volume(self):
        """计算体积（立方毫米）"""
        return float(self.length) * float(self.width) * float(self.height)

    @property
    def volume_m3(self):
        """计算体积（立方米）"""
        return self.volume / 1000000000
