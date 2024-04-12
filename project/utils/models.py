from django.db import models


class TimeBaseModel(models.Model):
    """
    抽象创建时间和更新时间
    """
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
