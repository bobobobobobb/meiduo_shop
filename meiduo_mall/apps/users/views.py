from django import http
from django.contrib.auth import login, logout
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views import View
import re

from apps.goods.models import SKU
from .models import User
from django.urls import reverse
import json
from utils.response_code import RETCODE
from celery_tasks.send_email.tasks import send_active_email
from .utils import check_token
from itsdangerous import BadSignature
from .models import Address
from django.contrib.auth.mixins import LoginRequiredMixin
from django_redis import get_redis_connection

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


# /addresses/create/    添加地址
class CreateAddressView(View):
    def get(self, request):
        pass

    def post(self, request):
        # 接受参数
        """
        title: '',
            receiver: '',
            province_id: '',
            city_id: '',
            district_id: '',
            place: '',
            mobile: '',
            tel: '',
            email: '',
        :param request:
        :return:
        """
        # b'{"title":"fsdfsdf","receiver":"fsdfsdf","province_id":440000,"city_id":440800,
        # "district_id":440882,"place":"fsdfdsd","mobile":"13068001213","tel":"","email":""}'
        # 判断 地址数量是否超过20
        if Address.objects.filter(is_deleted=0).count() >= 20:
            return JsonResponse({"code": RETCODE.DBERR, "errmsg": "添加地址失败"})
        body_data = request.body
        data = body_data.decode()
        import json
        address_dict = json.loads(data)
        title = address_dict["title"]
        receiver = address_dict["receiver"]
        province_id = address_dict["province_id"]
        city_id = address_dict["city_id"]
        district_id = address_dict["district_id"]
        place = address_dict["place"]
        mobile = address_dict["mobile"]
        tel = address_dict["tel"]
        email = address_dict["email"]

        # 校验数据
        if not all([title, receiver, province_id, city_id, district_id, place, mobile]):
            return HttpResponseBadRequest("参数不全")
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({"code": "4007"})
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return HttpResponseBadRequest('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return HttpResponseBadRequest('参数email有误')
                # 保存地址信息
        try:
            address = Address.objects.create(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
            # 设置默认地址
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()
        except Exception as e:
            # logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '新增地址失败'})

            # 新增地址成功，将新增的地址响应给前端实现局部刷新
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }
        #### 不能将一个对象传递给前端  对于ajax请求
        # 添加地址成功
        return JsonResponse({"code": RETCODE.OK, "address": address_dict})


# 展示地址   /show_address/
class ShowAddressView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        #####  先要检验用户是否登陆
        user = request.user
        # 查询出所有的地址
        addresses = Address.objects.filter(user=user, is_deleted=False)

        # 构造地址列表
        address_list = []
        for address in addresses:
            add_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "province_id": address.province_id,  ###  province_id  为隐藏属性
                "city": address.city.name,
                "city_id": address.city_id,
                "district": address.district.name,
                "district_id": address.district_id,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
                ### "is_deleted": address.is_deleted    已经进行了条件判断   这个属性不用传送
            }
            address_list.append(add_dict)

        context = {
            'default_address_id': user.default_address_id,  ###又见隐藏属性
            'addresses': address_list,
        }

        return render(request, 'user_center_site.html', context)  ### 向模板中传递字典


# 修改地址  路径  addresses/(?P<address_id>\d+)/$   方法:put
class UpdateAddressView(View):
    def put(self, request, address_id):
        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return HttpResponseBadRequest('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return HttpResponseBadRequest('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return HttpResponseBadRequest('参数email有误')

        # 判断地址是否存在,并更新地址信息
        try:
            Address.objects.filter(id=address_id).update(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
        except Exception as e:
            # 异常捕获需要写入日志
            # logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '更新地址失败'})

        # 构造响应数据
        address = Address.objects.get(id=address_id)
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 响应更新地址结果
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '更新地址成功', 'address': address_dict})


# 删除地址  /addresses/' + this.addresses[index].id + '/';   方式delete
class DeleteAddressView(View):
    def delete(self, request, address_id):
        # 判断该地址是否存在
        # 逻辑删除
        # 返回响应
        try:
            # 查询要删除的地址
            address = Address.objects.get(id=address_id)

            # 将地址逻辑删除设置为True
            address.is_deleted = True
            address.save()
        except Exception as e:
            # logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '删除地址失败'})

            # 响应删除地址结果
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '删除地址成功'})


# /addresses/' + this.addresses[index].id + '/default/'  put   设置默认地址
class SetDefaultAddressView(View):
    def put(self, request, address_id):
        # 查询该地址
        try:
            user = request.user
            address = Address.objects.get(id=address_id)

        except Address.DoesNotExist:
            return JsonResponse({"code": "1", "errmsg": "设置默认地址失败"})

        user.default_address_id = address.id
        user.save()
        return JsonResponse({"code": RETCODE.OK, "errmsg": "设置成功"})


class UpdateTitleAddressView(LoginRequiredMixin, View):
    """设置地址标题"""

    def put(self, request, address_id):
        """设置地址标题"""
        # 接收参数：地址标题
        json_dict = json.loads(request.body.decode())
        title = json_dict.get('title')

        try:
            # 查询地址
            address = Address.objects.get(id=address_id)

            # 设置新的地址标题
            address.title = title
            address.save()
        except Exception as e:
            # logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置地址标题失败'})

        # 4.响应删除地址结果
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '设置地址标题成功'})


class ChangePasswordView(LoginRequiredMixin, View):
    """修改密码"""

    def get(self, request):
        """展示修改密码界面"""
        return render(request, 'user_center_pass.html')

    def post(self, request):
        """实现修改密码逻辑"""
        # 1.接收参数
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        new_password2 = request.POST.get('new_password2')
        # 2.验证参数
        if not all([old_password, new_password, new_password2]):
            return HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^[0-9A-Za-z]{8,20}$', new_password):
            return HttpResponseBadRequest('密码最少8位，最长20位')
        if new_password != new_password2:
            return HttpResponseBadRequest('两次输入的密码不一致')

        # 3.检验旧密码是否正确
        if not request.user.check_password(old_password):
            return render(request, 'user_center_pass.html', {'origin_password_errmsg': '原始密码错误'})
        # 4.更新新密码
        try:
            request.user.set_password(new_password)
            request.user.save()
        except Exception as e:
            # logger.error(e)
            return render(request, 'user_center_pass.html', {'change_password_errmsg': '修改密码失败'})
        # 5.退出登陆,删除登陆信息
        logout(request)
        # 6.跳转到登陆页面
        response = redirect(reverse('users:login'))

        response.delete_cookie('username')

        return response


# browse_histories/  post  sku_id
class HistoryView(View):
    def post(self, request):
        dict_data = json.loads(request.body.decode())
        sku_id = dict_data['sku_id']

        ####### 接受数据的第一步就是验证数据
        try:
            SKU.objects.get(pk=sku_id)
        except SKU.DoesNotExist:
            return http.JsonResponse({'code': RETCODE.NODATAERR, 'errmsg': '没有此商品'})
        # 链接redis
        try:
            redis_conn = get_redis_connection('history')
            redis_conn.lrem('history:%s' % request.user.id, 0, sku_id)
            #     3.3 再添加
            # redis_conn.lpush(key,value)
            redis_conn.lpush('history:%s' % request.user.id, sku_id)
            #     3.4 列表中只保存5条记录
            # redis_conn.ltrim(key,start,stop)
            redis_conn.ltrim('history:%s' % request.user.id, 0, 4)
            # 4.返回相应
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok'})
        except Exception as e:
            return JsonResponse({'code': RETCODE.DBERR})

    def get(self, request):
        """
        browse_histories/
        get

        :param request:
        :return:
        """
        # 链接redis
        # 获取前五个数据
        # 查询该sku_id对应的相关信息 图片 名称  价格  url
        # 返回# 1.连接redis
        redis_conn = get_redis_connection('history')
        # 2.获取列表数据 [1,2,3,4]
        ids = redis_conn.lrange('history:%s' % request.user.id, 0, 4)
        # 3.根据id查询商品详情
        skus = []
        for id in ids:
            sku = SKU.objects.get(pk=id)
            # 4.组织json数据
            skus.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price,
            })
        # 5.返回相应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok', 'skus': skus})


