from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views import View
import re
from .models import User
from django.urls import reverse

"""
    1,获取数据
    2,校验数据的合法性
        2.1 校验用户名是否重复
        2.2 校验手机号
        2.3 校验两次密码是否一致
    3,存入数据库
    4,返回应答

"""


class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):

        # 1,获取数据
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        pic_code = request.POST.get('pic_code')
        # 2, 校验数据的合法性
        if not all([username, password, password2, mobile, pic_code]):
            return HttpResponseBadRequest('参数不全')

        # 2.1 校验用户名是否重复
            # 1,/register/username/count/
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}', username):
            return HttpResponseBadRequest('用户名格式不正确')
        # 2.2 校验手机号
        if not re.match(r'^1[1|3|5|7|8|9]\d{9}', mobile):
            return HttpResponseBadRequest('手机号格式不正确')
        # 2.3 校验两次密码是否一致
        if password != password2:
            return HttpResponseBadRequest('两次密码不一致')
        request.session.get

        # 3, 存入数据库
        try:
            User.objects.create_user(username=username,
                                     password=password,
                                     phone=mobile)
            return redirect(reverse('contents:index'))
        except Exception as e:
            return render(request, 'register.html', {'error':'你输入的信息有误，请重新注册！！！'})


class UsernameCount(View):
    def get(self, request, username):
        # 查询数据库
        count = User.objects.filter(username=username).count()
        # 返回响应
        return JsonResponse({'count': count})


class LoginView(View):
    def get(self, request):
        return render(request, '')





