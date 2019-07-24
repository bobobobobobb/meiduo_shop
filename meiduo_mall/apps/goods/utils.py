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


def get_breadcrumb(category):
    breadcrumb = {
        'cat1': '',
        'cat2': '',
        'cat3': '',
    }
    if category.parent is None:
        #     当前分类没有parent 最顶层的
        # 一级分类
        breadcrumb['cat1'] = category

    elif category.subs.count() == 0:

        #     当前分类没有子分类subs 最底层的
        # 三级分类
        breadcrumb['cat3'] = category
        breadcrumb['cat2'] = category.parent
        breadcrumb['cat1'] = category.parent.parent
    else:
        # 二级分类
        breadcrumb['cat2'] = category
        breadcrumb['cat1'] = category.parent

    return breadcrumb


def get_hot(category):
    skus = SKU.objects.filter(category=category, is_launched=True).order_by("-sales")[:2]
    # sku_list = []
    # for sku in skus:
    #     sku_list.append(sku)
    #
    # return JsonResponse({'code': RETCODE.OK, 'hot_skus': sku_list})
    skus_list = []
    # 2.将对象列表转换为字典数据   返回json数据, 对象列表时,需要将对象转换为字典
    for sku in skus:
        skus_list.append({
            'id': sku.id,
            'name': sku.name,
            'price': sku.price,
            'default_image_url': sku.default_image.url
        })

    return skus_list
