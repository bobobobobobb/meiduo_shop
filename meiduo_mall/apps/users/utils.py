# 设置手机号也能登陆  需要重写
from django.contrib.auth.backends import ModelBackend
from .models import User
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from meiduo_mall import settings


class UsernameMobileModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 因为密码被加密了, 所以无法获取到user对象

        # try:
        #     user = User.objects.get(username=username, password=password)
        #     if user:
        #         return user
        #     else:
        #         user = User.objects.get(phone=username, password=password)
        #         if user:
        #             return user
        #         else:
        #             user = None
        #             return user
        # except Exception as e:
        #     user = None
        #     return user


        # querydict 对象如果没有获取到, 值不空None


        # 获取不到user就会报错
        # try:
        #     user = None
        #     user = User.objects.get(username=username) or User.objects.get(phone=username)
        #     # if user is not None and user.check_password(password):
        #     if user is not None and user.check_password(password):
        #         return user
        #     else:
        #         user = User.objects.get(phone=username)
        #         if user is not None and user.check_password(password):
        #             return user
        # except Exception as e:
        #     user = None
        #     return user


        import re
        try:
            if re.match(r'1[3-9]\d{9}', username):

                user = User.objects.get(phone=username)

            else:

                user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        if user is not None and user.check_password(password):
            return user


# 对user.id 进行加密   给用户发送激活链接
def generate_active_url(user_id):
    s = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)
    data = {
        'user_id': user_id
    }
    token = s.dumps(data)
    return 'http://www.meiduo.site:8000/email_active/?token=%s' % token.decode()


# 对激活链接中的token进行解密
def check_token(token):
    s = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)
    user_id = s.loads(token)
    return user_id
