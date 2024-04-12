"""
重写 DRF Paginator
"""

from rest_framework import status as drf_status
from rest_framework.pagination import PageNumberPagination

from utils.response import APIResponse


class APIPageNumberPagination(PageNumberPagination):
    """
    分页 Page Number Paginator
    """
    # 默认每页大小
    page_size = 20
    # 每页最大数量
    max_page_size = 200
    # 自定义每页大小 字段
    page_size_query_param = 'size'
    # 自定义翻页 字段
    page_query_param = 'page'

    def get_paginated_response(self, data):
        return APIResponse(
            data=data,
            status=drf_status.HTTP_200_OK,
            msg='ok',
            next=self.get_next_link(),
            previous=self.get_previous_link(),
            count=self.page.paginator.count
        )
