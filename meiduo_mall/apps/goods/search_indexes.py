from haystack import indexes

from apps.goods.models import SKU


class SKUIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    # 对哪个模型进行全文检索
    def get_model(self):
        return SKU

    # 对哪些数据进行全文检索检索
    def index_queryset(self, using=None):
        return self.get_model().objects.filter(is_launched=True)
        # return SKU.objects.filter(is_launched=True)
        # return SKU.objects.all()
