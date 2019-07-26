from collections import OrderedDict

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
# Create your views here.
from apps.contents.models import ContentCategory
from apps.contents.utils import get_categories
from apps.goods.models import GoodsChannel
from .models import GoodsCategory, SKU
from utils.response_code import RETCODE

import json

from django import http
from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.contents.utils import get_categories
from apps.goods.models import GoodsCategory, SKU
from apps.goods.utils import get_breadcrumb, get_hot
from utils.response_code import RETCODE

"""
1. Docker 是没有可视化界面的虚拟机
2. 我们的虚拟机相当于一个一个的集装箱,集装箱中有我们需要的运行环境
3. Docker 是一个客户端-服务端(C/S)架构程序



安装docker客户端

镜像（Image）
    可以理解为: 虚拟环境
            安装系统的光盘/启动U盘

容器（Container）
    可以理解为: 运行起来的镜像

        一个镜像可以运行很多容器
        容器依赖于镜像




"""


# 列表页
class ListView(View):
    def get(self, request, category_id, page_num):

        # 检验该类别是否存在
        category_id = int(category_id)
        try:
            category = GoodsCategory.objects.get(id=category_id)

        except GoodsCategory.DoesNotExist:
            return render(request, '404.html', {'errmsg': '此类别不存在'})

        # 实现面包屑
        bread = get_breadcrumb(category)

        # 排序
        # 按照排序规则查询该分类商品SKU信息
        sort = request.GET.get('sort', 'default')
        if sort == 'price':
            # 按照价格由低到高
            sort_field = 'price'
        elif sort == 'hot':
            # 按照销量由高到低
            sort_field = '-sales'
        else:
            # 'price'和'sales'以外的所有排序方式都归为'default'
            sort = 'default'
            sort_field = 'create_time'

        # 查出该类别下的所有商品
        # skus = GoodsCategory.objects.sku_set.filter(is_launched=True)
        skus = SKU.objects.filter(category=category, is_launched=True).order_by(sort_field)

        # 进行分页
        try:
            paginator = Paginator(skus, 5)
            # 获取制定页数对象
            page_obj = paginator.page(page_num)
            # 获取总页数
            total_page = paginator.num_pages
        except Exception as e:
            return render(request, '404.html')

        sku_list = []
        for sku in skus:
            sku_list.append(sku)
        context = {
            'skus': sku_list,
            'total_page': total_page,
            'page_obj1': page_obj,
            'sort': sort,
            'bread': bread,
            'page_num': page_num,
            'category': category
        }

        # 返回应答
        return render(request, 'list.html', context)


# 热销    /hot/' + this.category_id + '/';
class Hot(View):
    def get(self, request, category_id):
        # 判断该总类是否存在
        try:
            category = GoodsCategory.objects.get(id=category_id)
        # 查出对应的ｓｋｕ商品，　并进行销量排序　取出前两个
        except GoodsCategory.DoesNotExist:
            return render(request, '404.html')

        skus_list = get_hot(category)

        # 3.返回JSON数据
        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok', 'hot_skus': skus_list})


"""
路径:  /detail/(?P<sku_id>\d+)/$    方式:GET
面包屑导航:调用:get_breadcrumb()
热销商品:调用get_hot()

"""


class DetailView(View):
    """商品详情页"""

    def get(self, request, sku_id):
        """提供商品详情页"""
        # 获取当前sku的信息
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return render(request, '404.html')

        # 查询商品频道分类
        categories = get_categories()
        # 查询面包屑导航
        breadcrumb = get_breadcrumb(sku.category)

        # 构建当前商品的规格键(查看当前商品都有那些规格)
        sku_specs = sku.specs.order_by('spec_id')
        sku_key = []
        for spec in sku_specs:
            sku_key.append(spec.option.id)
        # 获取当前商品的所有SKU (获取同一spu下的所有sku)

        skus = sku.spu.sku_set.all()
        # 构建不同规格参数（选项）的sku字典
        spec_sku_map = {}
        for s in skus:
            # 获取sku的规格参数
            s_specs = s.specs.order_by('spec_id')
            # 用于形成规格参数-sku字典的键
            key = []  # 当前商品规格值
            for spec in s_specs:
                key.append(spec.option.id)
            # 向规格参数-sku字典添加记录
            spec_sku_map[tuple(key)] = s.id
        # 获取当前商品应该有那些规格信息(通过spu查询)
        goods_specs = sku.spu.specs.order_by('id')
        # 若当前sku的规格信息不完整，则不再继续
        if len(sku_key) < len(goods_specs):
            return
        for index, spec in enumerate(goods_specs):
            # 复制当前sku的规格键
            key = sku_key[:]
            # 该规格的选项
            spec_options = spec.options.all()
            for option in spec_options:
                # 在规格参数sku字典中查找符合当前规格的sku
                key[index] = option.id

                if tuple(key) in spec_sku_map.keys():
                    option.sku_id = spec_sku_map[tuple(key)]
                else:
                    continue
                # option.sku_id = spec_sku_map.get(tuple(key))
            spec.spec_options = spec_options
            # <QuerySet [<SpecificationOption: Apple MacBook Pro 笔记本: 版本 - core i5/8G内存/256G存储>,
            # <SpecificationOption: Apple MacBook Pro 笔记本: 版本 - core i5/8G内存/128G存储>,
            # <SpecificationOption: Apple MacBook Pro 笔记本: 版本 - core i5/8G内存/512G存储>]>

        # 渲染页面
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'specs': goods_specs,
        }
        return render(request, 'detail.html', context)
