from django.db import models
from django.contrib.auth.models import AbstractUser
from utils.models import BaseModel


class User(AbstractUser):
    phone = models.CharField(max_length=20, unique=True)
    email_active = models.BooleanField(default=False)
    default_address = models.ForeignKey('Address', on_delete=models.SET_NULL, related_name='users', null=True, blank=True,
                                        verbose_name='默认地址')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class Address(BaseModel):
    """用户地址表"""
    # 用户id  收货人  所在地区   地址  手机 固定i电话  邮箱  是否默认   是否删除
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    receiver = models.CharField(max_length=50, verbose_name='收货人')
    title = models.CharField(max_length=20, verbose_name='地址名称')
    province = models.ForeignKey('area.Area', on_delete=models.PROTECT, related_name='province_addresses',
                                 verbose_name='省')
    city = models.ForeignKey('area.Area', on_delete=models.PROTECT, related_name='city_addresses', verbose_name='市')
    district = models.ForeignKey('area.Area', on_delete=models.PROTECT, related_name='district_addresses',
                                 verbose_name='区')
    place = models.CharField(max_length=50, verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
    email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='电子邮箱')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_address'
        verbose_name = '用户地址表'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']
