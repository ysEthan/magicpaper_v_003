from django.core.management.base import BaseCommand
from gallery.sync import ProductSync

class Command(BaseCommand):
    help = '清理旧的SKU图片'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='要清理多少天之前的图片'
        )

    def handle(self, *args, **kwargs):
        days = kwargs['days']
        sync = ProductSync()
        sync.clean_old_images(days)
        self.stdout.write(self.style.SUCCESS(f'成功清理{days}天前的旧图片')) 