"""
imgproxy
获取图片处理管道地址

imgproxy_url = imgproxy.get_img_url(img_path=obj.save_name, options=ImgProxyOptions.COVER_IMG)
"""

import hmac
import enum
import base64
import hashlib

from django.conf import settings


class ImgProxyOptions(enum.Enum):
    COVER_IMG = '/rs:fit:350:350/q:80'
    L_COVER_IMG = '/rs:fit:876:876/q:80'
    M_COVER_IMG = '/rs:fit:520:520/q:80'
    s_COVER_IMG = '/rs:fit:136:136/q:80'


class ImgProxy:
    def __init__(self, key, salt):
        self._key = bytes.fromhex(key)
        self._salt = bytes.fromhex(salt)

    def _get_signature(self, path):
        path = path.encode()
        digest = hmac.new(self._key, msg=self._salt + path, digestmod=hashlib.sha256).digest()
        signature = base64.urlsafe_b64encode(digest).rstrip(b"=")
        url = b'%s%s' % (signature, path)
        return url.decode()

    def get_img_url(self, img_path, options: ImgProxyOptions = ImgProxyOptions.COVER_IMG):
        source_url = f'{img_path}'
        base64_path = base64.b64encode(source_url.encode('utf-8')).decode('utf-8')
        url_path = self._get_signature(path=f'{options.value}/{base64_path}')
        return f'{settings.PROJ_IMAGE_BASE_URL}{url_path}'


imgproxy = ImgProxy(
    key=settings.IMGPROXY_KEY,
    salt=settings.IMGPROXY_SALT
)

if __name__ == '__main__':
    data = imgproxy.get_img_url('099c988eeb0c4c66851e4bdffa53d370.jpg', options=ImgProxyOptions.COVER_IMG)
    print(data)
