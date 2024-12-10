from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm

def home_page(request):
    menu_items = [
        {'name': '首页', 'url': '/'},
        {'name': '产品', 'url': '/products'},
        {'name': '服务', 'url': '/services'},
        {'name': '关于我们', 'url': '/about'},
        {'name': '联系方式', 'url': '/contact'},
    ]
    return render(request, 'home_page.html', {'menu_items': menu_items})

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # 表单验证
        if not all([username, email, password, confirm_password]):
            messages.error(request, '请填写所有必填字段')
            return redirect('register')
            
        if password != confirm_password:
            messages.error(request, '两次输入的密码不一致')
            return redirect('register')
            
        # 检查用户名是否已存在
        if User.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在')
            return redirect('register')
            
        # 检查邮箱是否已存在
        if User.objects.filter(email=email).exists():
            messages.error(request, '该邮箱已被注册')
            return redirect('register')
            
        # 创建新用户
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            messages.success(request, '注册成功！请登录')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'注册失败：{str(e)}')
            return redirect('register')
            
    return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            messages.success(request, '登录成功！')
            return redirect('home')  # 假设首页的 URL name 是 'home'
        else:
            messages.error(request, '用户名或密码错误')
    return render(request, 'login.html')
