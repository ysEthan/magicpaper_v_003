from django.core.management.base import BaseCommand
from gallery.models import Category

class Command(BaseCommand):
    help = '设置默认类目'

    def add_arguments(self, parser):
        parser.add_argument('category_id', type=int, help='要设置为默认的类目ID')

    def handle(self, *args, **options):
        try:
            category = Category.objects.get(id=options['category_id'])
            if not category.is_last_level:
                self.stdout.write(self.style.ERROR('指定的类目不是最后一级类目'))
                return
                
            # 可以在这里添加逻辑来标记默认类目
            category.is_default = True
            category.save()
            
            self.stdout.write(self.style.SUCCESS(f'成功设置类目 "{category.category_name_zh}" 为默认类目'))
            
        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'类目ID {options["category_id"]} 不存在')) 