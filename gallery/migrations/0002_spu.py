# Generated by Django 4.2.16 on 2024-12-10 13:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SPU',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='SPU ID')),
                ('spu_code', models.CharField(help_text='唯一的SPU标识码', max_length=50, unique=True, verbose_name='SPU编码')),
                ('spu_name', models.CharField(help_text='产品名称', max_length=200, verbose_name='SPU名称')),
                ('spu_remark', models.TextField(blank=True, help_text='产品描述或其他备注信息', null=True, verbose_name='备注')),
                ('sales_channel', models.IntegerField(choices=[(1, '线上'), (2, '线下'), (3, '全渠道')], default=3, help_text='产品销售渠道', verbose_name='销售渠道')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('status', models.BooleanField(default=True, help_text='是否启用', verbose_name='状态')),
                ('category', models.ForeignKey(help_text='产品所属类目', on_delete=django.db.models.deletion.PROTECT, related_name='spus', to='gallery.category', verbose_name='所属类目')),
            ],
            options={
                'verbose_name': 'SPU',
                'verbose_name_plural': 'SPU列表',
                'db_table': 'gallery_spu',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['spu_code'], name='gallery_spu_spu_cod_a8d7b0_idx'), models.Index(fields=['category'], name='gallery_spu_categor_15b940_idx'), models.Index(fields=['sales_channel'], name='gallery_spu_sales_c_8a819a_idx')],
            },
        ),
    ]
