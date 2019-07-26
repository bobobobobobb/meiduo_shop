import json
from django.utils import timezone
from django import http
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from decimal import Decimal
from apps.goods.models import SKU
from apps.users.models import Address
from utils.response_code import RETCODE
from .models import OrderInfo, OrderGoods


class PlaceOrderView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        """
        0, 登陆才能访问的页面
        1, 获取用户地址
        2, 获取支付方式
        3, 从redis中获取被选中商品的id   数量  遍历
        4, 查询该商品的相关信息   价格 名称 图片  计算总价格
        5, 返回响应数据
        :param request:
        :return:
        """
        # 1, 获取用户地址
        user = request.user
        # filter 获取不到数据会报错吗????????????????????????????????????????????
        address = Address.objects.filter(user=user, is_deleted=False)
        # 2, 获取支付方式
        # 支付方式是前端写死的,
        # 3, 从redis中获取被选中商品的id   数量  遍历
        try:
            redis_conn = get_redis_connection('cart')
            skus_dict = redis_conn.hgetall('cart:%s' % user.id)
            selected_skus = redis_conn.smembers('selected:%s' % user.id)
        except Exception as e:
            return http.HttpResponseBadRequest('error')
            # sku_list   接受对象
        skus_list = []
        total_count = 0
        total_amount = Decimal('0')
        feight = Decimal('0')
        for sku_id in selected_skus:
            sku = SKU.objects.get(id=sku_id)
            sku.total_count = int(skus_dict.get(sku_id))
            # 4, 查询该商品的相关信息   价格 名称 图片  计算总价格
            a = sku.price * sku.total_count
            sku.total_amount = Decimal(a)
            total_count += sku.total_count
            total_amount += sku.total_amount
            skus_list.append(sku)
        payment_amount = total_amount + 10
        # 5, 返回响应数据
        return render(request, 'place_order.html',
                      {'address': address, 'skus_list': skus_list, 'total_count': total_count,
                       'total_amount': total_amount, 'feight': 10, 'payment_amount': payment_amount})


class OrderCommitView(View):
    def post(self, request):
        """
        登陆才能访问
        保存订单信息和订单商品信息
        一, 保存订单信息
        1, 接受数据    支付方式   地址
        2, 校验数据   是否都传  地址是否存在   支付方式等
        3, 生成订单编号
        4, 获取当前时间

        5, 根据支付方式确认订单状态
        6, 确认总金额, 总数量, 运费

        二, 保存商品信息
        1, 链接redis 获取所有的sku_id
        2, 获取商品相关信息
        3, 判断库存是否充足
        4, 计算订单总金额, 数量
        5, 保存订单商品信息
        6, 更新订单信息
        7, 返回响应

        :param request:
        :return:
        """
        # 一, 保存订单信息
        # 1, 接受数据    支付方式   地址
        data = json.loads(request.body.decode())
        pay_method = data.get('pay_method')
        address_id = data.get('address_id')
        # 2, 校验数据   是否都传  地址是否存在   支付方式等
        if not all([pay_method, address_id]):
            return http.JsonResponse({'code': RETCODE.NODATAERR, 'errmsg': '数据补全'})

        # 判断地址是否存在
        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            pass

        # 判断支付方式
        try:
            pay_method = int(pay_method)
        except Exception as e:
            pass

        # 3, 生成订单编号
        # timezone.localtime().s
        # 4, 获取当前时间
        user = request.user
        order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + '%09d' % user.id
        # 5, 根据支付方式确认订单状态
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM["CASH"], OrderInfo.PAY_METHODS_ENUM["ALIPAY"]]:
            return http.JsonResponse({"code": RETCODE.NODATAERR})
        if pay_method == OrderInfo.PAY_METHODS_ENUM["CASH"]:
            # 货到付款
            status = OrderInfo.ORDER_STATUS_ENUM["UNRECEIVED"]
        else:
            # 支付宝
            status = OrderInfo.ORDER_STATUS_ENUM["UNSEND"]
        # 6, 确认总金额, 总数量, 运费
        # 无法计算总金额,先设为0
        total_amount = Decimal('0')
        total_count = 0
        freight = Decimal('0')
        # 为了防止丢失数据  在这里使用事务
        from django.db import transaction
        with transaction.atomic():
            # 如果出现问题,就回滚到这里
            save_point = transaction.savepoint()
        # 保存订单信息
            order = OrderInfo.objects.create(
                order_id=order_id,
                user=user,
                address=address,
                total_count=total_count,
                total_amount=total_amount,
                freight=freight,
                pay_method=pay_method,
                status=status
            )
            import time
            time.sleep(5)
            # 二, 保存商品信息
            # 1, 链接redis 获取所有的sku_id
            redis_conn = get_redis_connection('cart')
            skus_count_dict = redis_conn.hgetall('cart:%s' % user.id)
            skus_id = redis_conn.smembers('selected:%s' % user.id)
            cart = {}
            for sku_id in skus_id:

                cart[int(sku_id)] = int(skus_count_dict.get(sku_id))
            # 2, 获取商品相关信息
            ids = cart.keys()
            # skus = SKU.objects.filter(id__in=ids)
            for id in ids:
                sku = SKU.objects.get(id=id)
                # 3, 判断库存是否充足
                count = cart[sku.id]
                if count > sku.stock:
                    # 出现问题   开始回滚
                    transaction.savepoint_commit(save_point)
                    return http.JsonResponse({"code": RETCODE.STOCKERR, "errmsg": "%s库存补足" % sku.name})
                else:
                    # sku.stock -= count
                    # sku.sales = count
                    old_stock = sku.stock
                    new_stock = sku.stock - count
                    new_sales = count
                    # 更新
                    rect = SKU.objects.filter(id=sku.id, stock=old_stock).update(stock=new_stock, sales=new_sales)
                    if rect == 0:
                        # 表示失败
                        transaction.savepoint_rollback(save_point)
                        return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足'})
                    total_count += count
                    total_amount += sku.price * count

                    # 5, 保存订单商品信息
                    OrderGoods.objects.create(
                        order=order,
                        sku=sku,
                        count=count,
                        price=sku.price
                    )
            # 4, 计算订单总金额, 数量
            order.total_count = total_count
            order.total_amount = Decimal(total_amount)
            # 6, 更新订单信息
            order.save()
            transaction.savepoint_commit(save_point)
        # 7, 返回响应
        return http.JsonResponse({"code": RETCODE.OK,
                                  "order_id": order_id})


class OrderSuccess(View):
    def get(self, request):
        order_id = request.GET.get('order_id')
        payment_amount = request.GET.get('payment_amount')
        pay_method = request.GET.get('pay_method')

        context = {
            'order_id': order_id,
            'payment_amount': payment_amount,
            'pay_method': pay_method
        }
        return render(request, 'order_success.html', context)




