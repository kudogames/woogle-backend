"""
公用方法
"""

import secrets
import string


def short_uuid():
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(8))
