import re

from django.contrib.auth import login
from meiduo_mall import settings
from apps.users.models import User
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.http import JsonResponse, HttpResponseBadRequest
from QQLoginTool.QQtool import OAuthQQ
from django_redis import get_redis_connection
from .models import UserOpenid
from .utils import get_access_token, check_openid_token


class QAuthView(View):
    def get(self, request):
        # qq = OAuthQQ()
        # # return redirect('https://graph.qq.com/oauth2.0/authorize?response_type=code&client_id=101518219&redirect_uri=http://www.meiduo.site:8000/oauth_callback&state=test')
        # return JsonResponse({"url":'https://graph.qq.com/oauth2.0/authorize?response_type=code&client_id=101518219&redirect_uri=http://www.meiduo.site:8000/oauth_callback&state=test'})
        state = 'test'
        # 1.创建 OauthQQ实例
        qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                     client_secret=settings.QQ_CLIENT_SECRET,
                     redirect_uri=settings.QQ_REDIRECT_URI,
                     state=state)
        # 2.调用实例方法
        login_url = qq.get_qq_url()
        #
        return JsonResponse({'url': login_url})


class OauthCallBack(View):
    def get(self, request):
        try:
            # 获取code
            code = request.GET.get('code')

            # 通过code获取token
            qq = OAuthQQ(client_id='101518219',
                         client_secret='418d84ebdc7241efb79536886ae95224',
                         redirect_uri='http://www.meiduo.site:8000/oauth_callback')

            token = qq.get_access_token(code)

            # 获取openid
            open_id = qq.get_open_id(access_token=token)

            # 对openid进行加密
            token = get_access_token(open_id)

            # 判断openid是否存在
            try:
                qquser = UserOpenid.objects.get(open_id=open_id)
                login(request, qquser.user)

                response = redirect(reverse('contents:index'))
                response.set_cookie('username', qquser.user.username)
                return response
            except UserOpenid.DoesNotExist:
                return render(request, 'oauth_callback.html', {'open_id': token})
        except Exception as e:
            return redirect(reverse('users:login'))

    def post(self, request):
        # 接受数据 手机号 密码 短信验证码  openid
        phone = request.POST.get('mobile')
        password = request.POST.get('pwd')
        sms_code = request.POST.get('sms_code')
        open_id = request.POST.get('open_id')

        # 判断openid是否正确
        try:
            open_id = check_openid_token(open_id)
        except Exception as e:
            return HttpResponseBadRequest('数据被篡改了')

        # 数据是否全传过来
        if not all([phone, password, sms_code, open_id]):
            return HttpResponseBadRequest('参数不全')

        # 校验手机号格式
        if not re.match(r'^1[345678]\d{9}$', phone):
            return HttpResponseBadRequest('格式不正确')

        # 校验密码格式
        if not re.match(r'^[a-zA-Z0-9_]{8,20}$', password):
            return HttpResponseBadRequest('格式不正确')

        # 校验短信验证码正确性
        # 获取redis中的短信验证吗
        try:
            conn = get_redis_connection('verity')
            sms = conn.get('message:%s' % phone)
        except Exception as e:
            return HttpResponseBadRequest('短信验证码已经过期了')
        # 比对短信验证码
        if sms.decode() != sms_code:
            return HttpResponseBadRequest('你输入的短信验证码不正确')

        try:
            # 判断手机号是否注册
            user = User.objects.get(phone=phone)

            #######没有对用户进行密码检测
            if not user.check_password(password):
                return HttpResponseBadRequest('密码不正确')

        except User.DoesNotExist:
            # 尚未注册
            user = User.objects.create_user(password=password,
                                            phone=phone,
                                            username=phone)

            # 和open_id 进行绑定
        UserOpenid.objects.create(user=user, open_id=open_id)

        # 重定向到首页
        # 设置session
        login(request, user)
        response = redirect(reverse('contents:index'))
        response.set_cookie('username', user.username)
        return response



