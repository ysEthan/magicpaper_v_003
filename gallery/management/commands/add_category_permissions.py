from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from gallery.models import Category

class Command(BaseCommand):
    help = '给指定用户添加类目管理权限'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='要添加权限的用户名')

    def handle(self, *args, **options):
        username = options['username']
        try:
            user = User.objects.get(username=username)
            content_type = ContentType.objects.get_for_model(Category)
            permissions = Permission.objects.filter(content_type=content_type)
            
            for permission in permissions:
                user.user_permissions.add(permission)
                self.stdout.write(self.style.SUCCESS(
                    f'成功添加权限: {permission.codename} 给用户 {username}'
                ))
            
            user.save()
            self.stdout.write(self.style.SUCCESS(f'成功给用户 {username} 添加所有类目管理权限'))
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'用户 {username} 不存在')) 