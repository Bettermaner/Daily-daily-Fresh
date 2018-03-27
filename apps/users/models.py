
from django.contrib.auth.models import AbstractUser
from django.db import models
# Create your models here.
from tinymce.models import HTMLField

from DailyFresh import settings
from utils.models import BaseModel

from itsdangerous import TimedJSONWebSignatureSerializer


class User(BaseModel, AbstractUser):
    class Meta(object):
        db_table = 'df_user'

    def generate_active_token(self):
        serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 300)
        token = serializer.dumps({'confirm': self.id})
        return token.decode()


class Address(BaseModel):
    """地址"""

    receiver_name = models.CharField(max_length=20, verbose_name="收件人")
    receiver_mobile = models.CharField(max_length=11, verbose_name="联系电话")
    detail_addr = models.CharField(max_length=256, verbose_name="详细地址")
    zip_code = models.CharField(max_length=6, null=True, verbose_name="邮政编码")
    is_default = models.BooleanField(default=False, verbose_name='默认地址')

    user = models.ForeignKey(User, verbose_name="所属用户")

    class Meta:
        db_table = "df_address"


class TestModes(models.Model):
    ORDER_STATUS_CHOICES = (
        (1, '待支付'),
        (2, '待发货'),
        (3, '待收货'),
        (4, '待评论'),
        (3, '已完成'),

    )
    status = models.SmallIntegerField(default=1, verbose_name='订单状态', choices=ORDER_STATUS_CHOICES)

    class Meta(object):
        db_table = 'df_test'
        verbose_name = '测试模型'
        verbose_name_plural = verbose_name

    desc = HTMLField(verbose_name='商品描述', default='', null=True)
