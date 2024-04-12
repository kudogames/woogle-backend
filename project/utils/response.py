"""
重写 DRF Response
"""
from rest_framework.response import Response
from rest_framework import status as drf_status


class APIResponse(Response):
    def __init__(self, data=None, status=drf_status.HTTP_200_OK, msg='ok', headers=None, exception=False, **kwargs):
        res = {
            'msg': msg,
            **kwargs
        }
        if data is not None:
            res['data'] = data
        super().__init__(data=res, status=status, headers=headers, exception=exception)
