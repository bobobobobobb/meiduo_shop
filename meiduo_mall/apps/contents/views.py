from collections import OrderedDict

from django.shortcuts import render
from django.views import View

from apps.contents.models import ContentCategory
from .utils import get_categories

from apps.goods.models import GoodsChannel


class ErrorView(View):
    def get(self, request, error):
        return render(request, '404.html')


class IndexView(View):
    def get(self, request):
        """提供首页广告界面"""
        # 查询商品频道和分类
        categories = get_categories()

        # 广告数据
        contents = {}
        content_categories = ContentCategory.objects.all()
        for cat in content_categories:
            contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

        # 渲染模板的上下文
        context = {
            'categories': categories,
            'contents': contents,
        }
        return render(request, 'index.html', context)

# {'index_3f_bq': <QuerySet [<Content: 3楼标签: 厨具餐饮>, <Content: 3楼标签: 被子>,
# <Content: 3楼标签: 实木床>, <Content: 3楼标签: 箭牌马桶>, <Content: 3楼标签: 指纹锁>,
# <Content: 3楼标签: 电饭煲>, <Content: 3楼标签: 热水器>, <Content: 3楼标签: 席梦思>,
# <Content: 3楼标签: 沙发>]>, 'index_1f_cxdj': <QuerySet [<Content: 1楼畅享低价: 华为P10 全网通>,
# <Content: 1楼畅享低价: 小米 红米5 全网通版>, <Content: 1楼畅享低价: 魅蓝 Note6 全网通公开版>, <Content: 1楼畅享低价: 红米5Plus 全网通>, <Content: 1楼畅享低价: 荣耀9青春版 标配版>, <Content: 1楼畅享低价: 华为 畅享8 全网通>, <Content: 1楼畅享低价: 荣耀 畅玩7X 尊享版>, <Content: 1楼畅享低价: 华为 nova3e 全网通 幻夜黑>, <Content: 1楼畅享低价: 魅族 RPO 7 Plus 全网通>, <Content: 1楼畅享低价: 三星 S8 Plus 全网通>]>, 'index_3f_logo': <QuerySet [<Content: 3楼Logo: 水星家纺>]>, 'index_2f_jjhg': <QuerySet [<Content: 2楼加价换够: 小米九号平衡车>, <Content: 2楼加价换够: 小米空气净化器2>, <Content: 2楼加价换够: Apple Watch S3 GPS版>, <Content: 2楼加价换够: 裴讯智能体脂秤S7P>, <Content: 2楼加价换够: 360儿童手表电话SE2>, <Content: 2楼加价换够: S2PGHW-521蓝牙耳机>, <Content: 2楼加价换够: 科大讯飞 翻译机>, <Content: 2楼加价换够: Apple AirPods蓝牙耳机>, <Content: 2楼加价换够: ILIFE V5 智能扫地机器人>, <Content: 2楼加价换够: 360记录仪M301>]>, 'index_3f_shyp': <QuerySet [<Content: 3楼生活用品: 洁柔纸巾>, <Content: 3楼生活用品: 花仙子除湿剂>, <Content: 3楼生活用品: 超能洗衣液>, <Content: 3楼生活用品: 创简坊 扫帚>, <Content: 3楼生活用品: 万象玻璃杯>, <Content: 3楼生活用品: 爱丽丝收纳箱>, <Content: 3楼生活用品: 塑料袋 加厚>, <Content: 3楼生活用品: 特白惠 塑料杯>, <Content: 3楼生活用品: Bormioli Rocco意大利进口水果杯>, <Content: 3楼生活用品: 宜兴紫砂壶>]>, 'index_1f_bq': <QuerySet [<Content: 1楼标签: 荣耀手机>, <Content: 1楼标签: 国美手机>, <Content: 1楼标签: 华为手机>, <Content: 1楼标签: 热销推荐>, <Content: 1楼标签: 以旧换新>, <Content: 1楼标签: 潮3C>, <Content: 1楼标签: 全面屏>, <Content: 1楼标签: 守护宝>, <Content: 1楼标签: 存储卡>]>, 'index_1f_sjpj': <QuerySet [<Content: 1楼手机配件: Aogress一体双用数据线DC-28金>, <Content: 1楼手机配件: 黑客iPhone X 钢化膜>, <Content: 1楼手机配件: 黑客 3D曲面 全屏钢化膜>, <Content: 1楼手机配件: 三星（SAMSUNG）存储卡 64G>, <Content: 1楼手机配件: 浦诺菲(pivoful) PUC-15 Type-C 数据线>, <Content: 1楼手机配件: 好格(Aogress) A-100E移动电源>, <Content: 1楼手机配件: 卡士奇 存储卡>, <Content: 1楼手机配件: 捷波朗(Jabra)OTE23 运动蓝牙耳机>, <Content: 1楼手机配件: besiterBST-0109FO强尼思>]>, 'index_1f_pd': <QuerySet [<Content: 1楼频道: 手机>, <Content: 1楼频道: 配件>, <Content: 1楼频道: 充值>, <Content: 1楼频道: 优惠券>]>, 'index_2f_pd': <QuerySet [<Content: 2楼频道: 电脑>, <Content: 2楼频道: 数码>, <Content: 2楼频道: 配件>, <Content: 2楼频道: 潮电子>]>, 'index_1f_logo': <QuerySet [<Content: 1楼Logo: 荣耀V10>]>, 'index_2f_cxdj': <QuerySet [<Content: 2楼畅享低价: Apple iPad 平板电脑 2018款>, <Content: 2楼畅享低价: 华硕飞行堡垒五代游戏本>, <Content: 2楼畅享低价: ThinkPad T480>, <Content: 2楼畅享低价: 华硕飞行堡垒五代游戏本>, <Content: 2楼畅享低价: 艾比格特 无线移动WIFI>, <Content: 2楼畅享低价: 360 巴迪龙儿童手表>, <Content: 2楼畅享低价: Lenovo 星球大战 绝地挑战 AR眼镜>, <Content: 2楼畅享低价: HTC VR眼镜>, <Content: 2楼畅享低价: Apple Watch S3 蜂窝版>, <Content: 2楼畅享低价: 360电话手表 X1Pro>]>, 'index_lbt': <QuerySet [<Content: 轮播图: 美图M8s>, <Content: 轮播图: 黑色星期五>, <Content: 轮播图: 厨卫365>, <Content: 轮播图: 君乐宝买一送一>]>, 'index_3f_pd': <QuerySet [<Content: 3楼频道: 家具日用>, <Content: 3楼频道: 家纺寝具>, <Content: 3楼频道: 住宅家具>]>, 'index_kx': <QuerySet [<Content: 快讯: i7顽石低至4199元>, <Content: 快讯: 奥克斯专场 正1匹空调1313元抢>, <Content: 快讯: 荣耀9青春版 高配 领券立减220元>, <Content: 快讯: 美多探索公益新模式>, <Content: 快讯: 冰箱洗衣机专场 套购9折>, <Content: 快讯: 超市美食家 满188减100>, <Content: 快讯: 电竟之日 电脑最高减1000元>]>, 'index_1f_ssxp': <QuerySet [<Content: 1楼时尚新品: 360手机 N6 Pro 全网通>, <Content: 1楼时尚新品: iPhone X>, <Content: 1楼时尚新品: 荣耀 畅玩7A 全网通 极光蓝>, <Content: 1楼时尚新品: 魅蓝 S6 全网通>, <Content: 1楼时尚新品: 红米5Plus 全网通 浅蓝>, <Content: 1楼时尚新品: OPPO A1 全网通 深海蓝>, <Content: 1楼时尚新品: 华为 nova3e 全网通 幻夜黑>, <Content: 1楼时尚新品: OPPO R15 全网通 梦镜红>, <Content: 1楼时尚新品: 荣耀V10 全网通 标配版 沙滩金>, <Content: 1楼时尚新品: vivo X21 异形全面屏 全网通>]>, 'index_ytgg': <QuerySet [<Content: 页头广告: 好友联盟双双赚>]>, 'index_2f_bq': <QuerySet [<Content: 2楼标签: iPad新品>, <Content: 2楼标签: 限量购>, <Content: 2楼标签: 单反相机>, <Content: 2楼标签: 智能家具>, <Content: 2楼标签: 智能路由>, <Content: 2楼标签: 限时抢>, <Content: 2楼标签: 颂拓>, <Content: 2楼标签: 微单>, <Content: 2楼标签: 耳机>]>, 'index_3f_cfyp': <QuerySet [<Content: 3楼厨房用品: 苏泊尔 炒锅>, <Content: 3楼厨房用品: 双立人 多用双刀>, <Content: 3楼厨房用品: 爱仕达高压锅>, <Content: 3楼厨房用品: 维艾圆形不秀钢盆>, <Content: 3楼厨房用品: 家栢利304不锈钢壁挂>, <Content: 3楼厨房用品: 生物海瓷>, <Content: 3楼厨房用品: 实木筷>, <Content: 3楼厨房用品: 菜板>, <Content: 3楼厨房用品: 刻度玻璃瓶>, <Content: 3楼厨房用品: 韩国进口 密封盒>]>, 'index_2f_logo': <QuerySet [<Content: 2楼Logo: 小米笔记本Air>]>}
