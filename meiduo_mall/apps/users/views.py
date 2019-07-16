from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views import View
import re
from .models import User
from django.urls import reverse
import json
from utils.response_code import RETCODE
from celery_tasks.send_email.tasks import send_active_email
from .utils import check_token
from itsdangerous import BadSignature

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
            return render(request, 'register.html', {'error': '你输入的信息有误，请重新注册！！！'})


class UsernameCount(View):
    def get(self, request, username):
        # 查询数据库
        count = User.objects.filter(username=username).count()
        # 返回响应
        return JsonResponse({'count': count})


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        # 接受数据  用户名 密码 是否记住登陆状态
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        remembered = request.POST.get('remembered')
        next_url = request.GET.get('next')

        # 校验数据的合法性
        # 判断数据是否不全
        if not all([username, password]):
            return HttpResponseBadRequest('参数不全')

        # 判断用户名
        if not re.match(r'^[a-zA-Z0-9_]{5,20}', username):
            return HttpResponseBadRequest('用户名不合法')

        # 判断密码
        # if not re.match(r'^[a-zA-Z0-9_]{8,20}', password):
        #     return HttpResponseBadRequest('密码不合法')

        # 校验该用户是否已经注册
        from django.contrib.auth import authenticate
        user = authenticate(username=username, password=password)

        # 验证不通过
        if user is None:
            return HttpResponseBadRequest('用户名或密码不正确')

        # 记住登陆状态
        login(request, user)
        # 判断是否记住登陆状态
        if remembered:
            request.session.set_expiry(None)
        else:
            request.session.set_expiry(0)

        # 如果next不为空
        if next_url:
            response = redirect(next_url)
        else:
            response = redirect(reverse('contents:index'))

        # 设置cookie
        response.set_cookie('username', username, None)
        # 返回应答
        return response


class LogoutView(View):
    def get(self, request):
        logout(request)
        response = redirect(reverse('contents:index'))
        response.delete_cookie('username')
        return response


from django.contrib.auth.mixins import LoginRequiredMixin


class UserCenterView(LoginRequiredMixin, View):
    # 两种方式   一种设置login_url    一种设置settings.LOGIN_URL
    login_url = '/login/'

    def get(self, request):

        # 查询用户名  手机号 email
        user = request.user
        try:
            user = User.objects.get(username=user.username)
        except Exception as e:
            return HttpResponseBadRequest('系统故障')

        # 组织模板上下文
        context = {
            'username': user.username,
            'mobile': user.phone,
            'email': user.email
        }
        return render(request, 'user_center_info.html', context)


# 向用户发送邮件
class SendEmailView(View):
    # 　发送邮件
    def put(self, request):
        # 接受参数   邮箱
        # 校验邮箱
        # 当用户点击保存邮箱的时候  前段发起ajax请求  后端更新用户数据   返回应答  保存按钮变为已保存状态 不可选取
        # 接受参数   邮箱
        body = request.body
        body_str = body.decode()
        # import json
        body_dict = json.loads(body_str)
        # 获取邮箱
        email = body_dict['email']
        send_active_email(email, request.user.id)
        return JsonResponse({'code': RETCODE.OK})

    # 保存邮箱到数据库
    def post(self, request):
        # 接受参数   邮箱
        body = request.body
        body_str = body.decode()
        # import json
        body_dict = json.loads(body_str)
        # 获取邮箱
        email = body_dict['email']
        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return JsonResponse({'code': RETCODE.EMAILERR})
        user = request.user
        user.email = email
        user.save()
        # 保存成功 返回应答
        return JsonResponse({'code': RETCODE.OK})

    # 更换已经绑定的邮箱
    def get(self, request):
        user = request.user
        user.email = ''
        user.save()
        return JsonResponse({'code': RETCODE.OK})


# 激活链接
class ActiveUrlView(View):
    def get(self, request):
        token = request.GET.get('token')
        # 对token进行解密
        try:
            user_id = check_token(token)
        except BadSignature:
            # 激活失败  重新发送邮件
            email = request.user.email
            send_active_email(email, request.user.id)
            return HttpResponseBadRequest('激活失败,请去邮箱重新进行激活')

        # 激活成功
        user = User.objects.get(id=user_id['user_id'])
        user.email_active = 1
        user.save()
        # return HttpResponse('激活邮箱成功')
        return redirect('users:center')


class SeeStateView(View):
    def get(self, request):
        user = request.user
        if user.email_active:
            return JsonResponse({'code': RETCODE.OK})
        else:
            return JsonResponse({'code': 1})


class UserCenterSiteView(View):
    def get(self, request):
        return render(request, 'user_center_site.html')
