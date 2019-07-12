from django.shortcuts import render
from django.views import View
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from .constants import IMAGE_EXPIRE_TIME
from django.http import JsonResponse, HttpResponse
from utils import response_code
from libs.yuntongxun.sms import CCP


class VerifyView(View):
    def get(self, request, uuid):
        code, image = captcha.generate_captcha()

        # 连接redis数据库
        conn = get_redis_connection('verity')

        # 将图片验证码保存到redis中 并设置过期时间
        conn.setex('img:%s' % uuid, IMAGE_EXPIRE_TIME, code)
        # codes = conn.get('img:uuid')

        # 将生成的图片验证码进行返回
        return HttpResponse(image, content_type='image/jpeg')


class GetSmsView(View):
    def post(self, request):
        # 接受发送过来的数据
        data = request.body
        data = data.decode()
        import json
        # 转换为字典
        data1 = json.loads(data)

        # 获取uuid
        uuid = data1['uuid']

        # 获取手机号
        mobile = data1['mobile']

        # 获取用户输入的验证码
        pic_code = data1['pic_code']

        # 连接redis, 获取图片验证码
        try:
            conn = get_redis_connection('verity')
            # 检查用户是否多次发送
            send_flag = conn.get('send_flag:%s' % mobile)

            # 从redis中取出来的值为bytes类型, 需要进行解码才能进行判断
            if send_flag is not None and send_flag.decode() == '1':
                return JsonResponse({'code': response_code.RETCODE.THROTTLINGERR})

            image_code = conn.get('img:%s' % uuid)
        except Exception as e:
            return JsonResponse({"code": response_code.RETCODE.DBERR})

        else:
            # 比对图片验证码
            if pic_code.lower() != image_code.decode().lower():
                return JsonResponse({"code": response_code.RETCODE.IMAGECODEERR})

            # 生成短信验证码
            import random
            message = '%d' % random.randint(0, 999999)

            # 讲短信验证密进行保存(保存五分钟) 并且保存发送标记(第一次发送)  在这里使用管道
            pl = conn.pipeline()
            pl.setex('message:%s' % mobile, 60 * 5, message)
            pl.setex('send_flag:%s' % mobile, 60 * 5, 1)
            pl.execute()

            # 发送验证码
            # CCP().send_template_sms(18801315163, [message, 5], 1)

            # 使用celery异步发送短信
            from celery_tasks.sms.tasks import send_sms
            send_sms(13068001619, message)

            # 返回应答
            return JsonResponse({"code": 1})


class CheckMObileView(View):
    def post(self, request):
        # 接受参数
        data = request.body
        data1 = data.decode()
        import json
        data1 = json.loads(data1)

        # 获取手机号
        mobile = data1["mobile"]

        # 校验手机号是否合法
        from apps.users.models import User
        count = User.objects.filter(phone=mobile).count()

        # 返回应答 根据count值进行判断
        return JsonResponse({'code': count})
