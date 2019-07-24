# 登陆状态下展示登陆界面
from django_redis import get_redis_connection

from apps.goods.models import SKU


def show_online_cart(user):
    # 链接redis
    redis_conn = get_redis_connection('cart')
    # 返回字典{sku_id: count}
    skus = redis_conn.hgetall("cart:%s" % user.id)
    # 返回列表
    selected_id = redis_conn.smembers("selected:%s" % user.id)
    sku_list = []
    # 对该字典进行遍历  查出商品的相关信息
    for sku_id, count in skus.items():

        sku = SKU.objects.get(id=sku_id)
        sku.count = int(count)
        if sku_id in selected_id:
            sku.selected = True
        else:
            sku.selected = False

        sku_list.append({
            "id": sku.id,
            "name": sku.name,
            "default_image_url": sku.default_image.url,
            "price": str(sku.price),
            "count": sku.count,
            "selected": str(sku.selected)
        })

    return sku_list


