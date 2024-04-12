from django.http import Http404
from django.conf import settings


def api_auth(func):
    """
    装饰器
    验证 API Token
    """

    def wrapper(request, *args, **kwargs):
        access_token = settings.AUTH_TOKEN
        request_auth_token = request.META.get('HTTP_AUTHORIZATION')
        if request_auth_token != access_token:
            raise Http404('Not Found')
        else:
            return func(request, *args, **kwargs)

    return wrapper
