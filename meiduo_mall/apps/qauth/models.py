from django.db import models
from utils.models import BaseModel


class UserOpenid(BaseModel):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='用户')
    open_id = models.CharField(max_length=50, verbose_name='open_id', db_index=True)

    class Meta:
        db_table = 'tb_auth_qq'
        verbose_name = 'QQ登陆用户数据'
        verbose_name_plural = verbose_name
