import json

from django import http
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

# g购物车
from django_redis import get_redis_connection

from apps.carts.utils import show_online_cart
from apps.goods.models import SKU
from utils.response_code import RETCODE
import pickle
import base64


class CartView(View):
    # 　展示购物车
    def get(self, request):
        """
        1,判断用户是否登陆
            1)登陆情况下:
                从redis中获取商品相关记录sku_id　遍历
                查询处商品的其他信息
                从cookie中获取为登陆情况下购物车中的商品


            2)未登录
                从cookie中获取
                查询
        2,返回
        :param request:
        :return:
        """
        # 1, 判断用户是否登陆
        user = request.user
        if user is not None and user.is_authenticated:
            # 1)登陆情况下:
            # 合并购物车  获取cookie
            cart = request.COOKIES.get("goods")
            if cart is not None:
                # 对数据进行解密
                try:
                    cart = pickle.loads(base64.b64decode(cart))
                    # 链接redis 获取所有的sku_id
                    redis_conn = get_redis_connection('cart')
                    redis_dict = redis_conn.hgetall('cart:%s' % user.id)
                    # dui cookie进行遍历
                    for sku_id, selected_count in cart.items():
                        # 获取cookie中的count
                        cookie_count = selected_count['count']
                        if sku_id in redis_dict:
                            # 和redis中的count进行合并
                            redis_conn.hincrby('cart:%s' % user.id, sku_id, cookie_count)
                        else:
                            redis_conn.hset('cart:%s' % user.id, sku_id, cookie_count)

                        # 合并状态  以cookie中的为准
                        if selected_count["selected"]:
                            redis_conn.sadd('selected:%s' % user.id, sku_id)
                        else:
                            redis_conn.srem('selected:%s' % user.id, sku_id)

                    # 合并成功 返回响应  展示购物车的时候,需要向前端传送数据
                    sku_list = show_online_cart(user)
                    # 删除cookie
                    response = render(request, "cart.html", {"cart_skus": sku_list})
                    response.delete_cookie('goods')
                    return response

                # cookie中数据出现异常
                except Exception as e:
                    # 就不合并了
                    sku_list = show_online_cart(user)
                    return render(request, "cart.html", {"cart_skus": sku_list})

            else:
                # cookie中没有记录的时候
                sku_list = show_online_cart(user)
                return render(request, "cart.html", {"cart_skus": sku_list})

        else:

            # 2)未登录
            # 从cookie中获取
            cart = request.COOKIES.get("goods")
            sku_list = []
            if cart:
                # 解码
                cart = pickle.loads(base64.b64decode(cart))
                # 查询  遍历获取
                # sku_list = []
                for sku_id, sku_dic in cart.items():
                    sku = SKU.objects.get(id=sku_id)
                    sku.count = sku_dic["count"]
                    sku.selected = sku_dic["selected"]
                    sku_list.append({
                        "id": sku.id,
                        "name": sku.name,
                        "default_image_url": sku.default_image.url,
                        "price": str(sku.price),
                        "count": sku.count,
                        "selected": str(sku.selected)
                    })
                    # context = {
                    #     "sku_list": sku_list
                    # }
                    # 2, 返回

            return render(request, 'cart.html', {"cart_skus": sku_list})

            # return render(request, 'cart.html')
            # else:
            #     # 3.未登录用户从cookie中获取数据
            #     #     3.1 读取cookie中数据,并进行判断  {sku_id:{'count':xxx,'selected':True}}
            #     carts_cookie = request.COOKIES.get('carts')
            #     if carts_cookie is not None:
            #         de = base64.b64decode(carts_cookie)
            #         carts = pickle.loads(de)
            #     else:
            #         carts = {}
            #
            #         #  获取商品id
            #         # {sku_id:{'count':xxx,'selected':True}}
            #
            # ids = carts.keys()  # [1,2,3,4,5,6,7]
            # sku_list = []
            # # 4 对商品id进行遍历
            # for id in ids:
            #     # 5 根据id获取商品的详细信息
            #     sku = SKU.objects.get(pk=id)
            #     # 6 将对象转换为字典
            #     sku_list.append({
            #         'id': sku.id,
            #         'name': sku.name,
            #         'count': carts.get(sku.id).get('count'),
            #         'selected': str(carts.get(sku.id).get('selected')),  # 将True，转'True'，方便json解析
            #         'default_image_url': sku.default_image.url,
            #         'price': str(sku.price),  # 从Decimal('10.2')中取出'10.2'，方便json解析
            #         'amount': str(sku.price * carts.get(sku.id).get('count')),
            #     })
            # # 7 返回相应
            # context = {
            #     'cart_skus': sku_list
            # }
            # return render(request, 'cart.html', context=context)

    """
    数据: sku_id, count, selected
    post
    carts/
    1,接受数据
        数据: sku_id, count, selected
    2,检验数据
        1)商品是否存在
        2)是否全部传过来
        3)count能否转换为整数
    3,保存到数据库
        redis
        mysql
        1) 用户登陆
            redis
                user_id, sku_id, count, selected
                这里选用hash: key:user_id    sku_id: count   正数代表被选中,负数代表未被选中

        2)未登录
            cookie
            数据: sku_id, count, selected
            {sku_id_1:{
                        count:  xxx,
                        selected: true},
            sku_id_2:{
                        count:  xxx,
                        selected: true},
            ....

            }
            加密
            设置cookie
    4,返回响应

    :param request:
    :return:
    """

    def post(self, request):
        # 0.接收数据,验证数据
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        count = data.get('count')
        selected = data.get('selected', True)

        user = request.user
        if not all([sku_id, count]):
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '参数错误'})

        try:
            sku = SKU.objects.get(pk=sku_id)
        except SKU.DoesNotExist:
            return http.JsonResponse({'code': RETCODE.NODATAERR, 'errmsg': '没有此商品'})

        try:
            count = int(count)
        except Exception as e:
            # 用户输入了字母,  需要转换为1
            count = 1

        # 判断用户是否登陆
        if user is not None and user.is_authenticated:
            # 用户已经登陆
            redis_conn = get_redis_connection('cart')
            if selected:
                #################一个很傻逼的错误    redis键不能重复
                # conn.hset("%s" % user.id, "%s" % sku_id, count)
                # conn.hset('carts:%s' % user.id, sku_id, count)
                # # sadd key member1 member2 ...
                # # conn.sadd("%s" % user.id, "%s" % sku_id)
                # conn.sadd('selected:%s' % user.id, sku_id)
                # 使用管道
                pipeline = redis_conn.pipeline()
                pipeline.hincrby("cart:%s" % user.id, sku_id, count)
                pipeline.sadd("selected:%s" % user.id, sku_id)
                pipeline.execute()
            else:
                redis_conn.hset("cart:%s" % user.id, sku_id, count)

            return JsonResponse({"code": RETCODE.OK})
        else:
            # 用户未登录
            response = JsonResponse({'code': RETCODE.OK})
            # 加密
            # 构造数据
            # 从cookie中获取数据
            # ###########  老师没讲看是否有值
            data = request.COOKIES.get('goods')
            if selected:
                selected = False
            else:
                selected = True
            if data:
                goods_dict = pickle.loads(base64.b64decode(data))
                # 　更新数量
                if sku_id in goods_dict:
                    # {sku_id:{count: xxx, selected: xxx}
                    # goods_dict[sku_id]['count'] = goods_dict[sku_id]['count'] + count
                    origin_count = goods_dict[sku_id]["count"]
                    count += origin_count

                goods_dict[sku_id] = {
                    "count": count,
                    "selected": selected
                }
            else:
                goods_dict = {}
                goods_dict[sku_id] = {
                    "count": count,
                    "selected": selected
                }
            # 加密
            data = pickle.dumps(goods_dict)
            data = base64.b64encode(data)

            response.set_cookie("goods", data, 3600)
            return response

    def put(self, request):
        """
        1,修改购物车   商品状态   数量    put   sku_id    ajax
        2, 校验数据合法性   数量是否为整数  该商品是否存在  数据是否全部传送
        3, 用户登陆
            1) 获取redis中所有的sku_id列表
            2) 判断sku_id是否在这个列表中
            3) 存在直接覆盖掉
            4) selected如果为true, 添加到集合中
            5) false   在该集合中删除sku_id
            6) 返回响应
        4,未登录
            1) 读取cookie
            2) 遍历所有的键
            3) 存在 直接覆盖
            4) 返回响应

        :param request:
        :return:
        """
        # 1, 修改购物车  商品状态  数量  put  sku_id   ajax
        # 2, 校验数据合法性   数量是否为整数  该商品是否存在  数据是否全部传送
        data = json.loads(request.body.decode())
        count = data.get('count')
        sku_id = data.get('sku_id')
        selected = data.get('selected')
        if not all([count, sku_id]):
            return http.JsonResponse({'code': RETCODE.NODATAERR})

        if count < 0:
            return http.JsonResponse({'code': RETCODE.NODATAERR})
        try:
            count = int(count)
        except Exception as e:
            count = 1
        try:
            sku = SKU.objects.get(pk=sku_id)
        except SKU.DoesNotExist:
            return http.JsonResponse({'code': RETCODE.NODATAERR})
        # 3, 用户登陆
        user = request.user
        if user is not None and user.is_authenticated:
            #     1) 获取redis中所有的sku_id列表
            redis_conn = get_redis_connection('cart')
            if count == 0:
                redis_conn.hdel('cart:%s' % user.id, sku_id)

                redis_conn.srem('cart:%s' % user.id, sku_id)

            else:
                #     3) 存在直接覆盖掉
                redis_conn.hset('cart:%s' % user.id, sku_id, count)
                if not selected:
                    #     4) selected如果为true, 添加到集合中
                    redis_conn.sadd('selected:%s' % user.id, sku_id)
                else:
                    #     5) false   在该集合中删除sku_id
                    try:
                        redis_conn.srem('selected:%s' % user.id, sku_id)

                    except Exception as e:
                        print(e)

            #     6) 返回响应
            selected = True
            cart_sku = {
                "id": sku.id,
                "name": sku.name,
                "default_image_url": sku.default_image.url,
                "price": str(sku.price),
                "count": count,
                "selected": str(selected)
            }

            return http.JsonResponse({"code": RETCODE.OK, "cart_sku": cart_sku})
        # 4,未登录
        else:
            #     1) 读取cookie
            data = request.COOKIES.get('goods')
            # 解密
            cart = pickle.loads(base64.b64decode(data))
            #     2) 遍历所有的键
            #     3) 存在 直接覆盖
            if selected:
                selected = False
            else:
                selected = True
            cart[sku_id] = {
                "count": count,
                "selected": selected
            }

            cart_sku = {
                "id": sku.id,
                "name": sku.name,
                "default_image_url": sku.default_image.url,
                "price": str(sku.price),
                "count": count,
                "selected": selected
            }
            # 加密
            data = base64.b64encode(pickle.dumps(cart))
            response = JsonResponse({'code': RETCODE.OK, 'cart_sku': cart_sku})
            response.set_cookie('goods', data, max_age=3600)
            #     4) 返回响应
            return response

    def delete(self, request):
        """
        接受数据   post   sku_id
        检验数据
        登陆状态
        未登录状态

        返回响应    不需要给前段返回数据
        :param request:
        :return:
        """
        # 接收数据
        data = json.loads(request.body.decode())
        sku_id = data.get("sku_id")

        # 校验数据   该种类水否存在
        try:
            sku = SKU.objects.get(id=sku_id)

        except SKU.DoesNotExist:
            return JsonResponse({'code': RETCODE.NODATAERR})

        # 登陆状态
        user = request.user

        if user is not None and user.is_authenticated:
            # 链接redis
            redis_conn = get_redis_connection('cart')
            # redis_conn.hdel('cart:%s' % user.id, sku_id)
            # redis_conn.srem('selected:%s' % user.id, sku_id)

            # 删除
            pipeline = redis_conn.pipeline()
            pipeline.hdel('cart:%s' % user.id, sku_id)
            pipeline.srem('selected:%s' % user.id, sku_id)
            pipeline.execute()

            # 返回响应
            return JsonResponse({'code': RETCODE.OK})
        # 未登录
        else:
            # 从cookie中获取数据
            data = request.COOKIES.get('goods')

            # 解密
            cart = pickle.loads(base64.b64decode(data))

            # 删除
            del cart[sku_id]

            # 加密
            cart = base64.b64encode(pickle.dumps(cart))

            response = JsonResponse({'code': RETCODE.OK})

            # 设置cookie
            response.set_cookie('goods', cart, max_age=3600)

            return response


# 设置购物车全选
class SelectAllCartView(View):
    def put(self, request):
        """
        不需要给前端返回数据

        1,接受数据selected
        2,校验数据 是否是bool类型
        3,登陆状态
        4,未登录状态
        5,返回响应
        :param request:
        :return:
        """
        data = json.loads(request.body.decode())

        selected = data.get("selected")

        if not isinstance(selected, bool):
            return JsonResponse({"code": RETCODE.NODATAERR})

        # 登陆状态
        user = request.user
        if user is not None and user.is_authenticated:
            # 链接redis
            redis_conn = get_redis_connection('cart')
            # pipeline = redis_conn.pipeline()

            # 得到所有的sku_id
            sku_dict = redis_conn.hgetall('cart:%s' % user.id)
            for sku_id in sku_dict.keys():
                if selected:
                    redis_conn.sadd('selected:%s' % user.id, sku_id)
                else:
                    redis_conn.srem('selected:%s' % user.id, sku_id)

            return JsonResponse({"code": RETCODE.OK})

        # 未登录状态
        else:
            # 读取cookie
            data = request.COOKIES.get('goods')

            # 解密
            cart_dict = pickle.loads(base64.b64decode(data))

            if selected:
                # 设置selected为false
                for select in cart_dict.values():
                    select["selected"] = True

            else:
                for select in cart_dict.values():
                    select["selected"] = False

            # 加密
            cart_dict = base64.b64encode(pickle.dumps(cart_dict))
            response = JsonResponse({"code": RETCODE.OK})
            response.set_cookie('goods', cart_dict, max_age=3600)
            # 返回响应
            return response


class ShowSimpleCartView(View):
    def get(self, request):
        """
        1,登陆状态
            1.1 读取redis  获取skus
            1.2 遍历获取商品相关信息
            1.3 传送字典列表数据给前端
        2,未登录状态
            2.1 读取cookie
            2.2 解密
            2.3 获取skus
            2.4 遍历获取商品信息
            2.5 组织数据
            2.6 返回数据
        :param request:
        :return:
        """
        # 1,登陆状态
        user = request.user
        if user is not None and user.is_authenticated:
            # 1.1 读取redis  获取skus
            redis_conn = get_redis_connection('cart')
            skus_dict = redis_conn.hgetall('cart:%s' % user.id)
            cart_dict = {}
            for sku_id, count in skus_dict.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count)
                }

        # 2,未登录状态
        else:
            # 2.1 读取cookie
            cart = request.COOKIES.get('goods')
            if cart:
                # 2.2 解密
                cart_dict = pickle.loads(base64.b64decode(cart))
            else:
                cart_dict = {}
        # 2.3 获取skus
        sku_list = []
        for sku_id in cart_dict:
            # 1.2 遍历获取商品相关信息
            sku = SKU.objects.get(id=sku_id)
            # 1.3 传送字典列表数据给前端
            sku_list.append({
                'id': sku.id,
                'name': sku.name,
                'count': cart_dict.get(sku.id).get('count'),
                'default_image_url': sku.default_image.url
            })

        # 返回
        return JsonResponse({"code": RETCODE.OK, "cart_skus": sku_list})














