from django.core import signing
import hashlib
from django.core.cache import cache
import time
import jwt
import os

HEADER = {'typ': 'JWP', 'alg': 'default'}
KEY = 'GAMIFICATION'
SALT = 'gamification_platform'
TIME_OUT = 30 * 60  # 30min


def get_user_pk(request):
    token = request.META.get('HTTP_AUTHORIZATION').split()[1]
    token_data = jwt.decode(token, os.getenv('SECRET_KEY'), algorithm='HS256')
    return token_data['id']


def encrypt(obj):
    value = signing.dumps(obj, key=KEY, salt=SALT)
    value = signing.b64_encode(value.encode()).decode()
    return value


def decrypt(src):
    src = signing.b64_decode(src.encode()).decode()
    raw = signing.loads(src, key=KEY, salt=SALT)
    return raw


def create_token(username):
    header = encrypt(HEADER)
    payload = {"username": username, "iat": time.time()}
    payload = encrypt(payload)
    md5 = hashlib.md5()
    md5.update(("%s.%s" % (header, payload)).encode())
    signature = md5.hexdigest()
    token = "%s.%s.%s" % (header, payload, signature)
    cache.set(username, token, TIME_OUT)
    return token


def get_payload(token):
    payload = str(token).split('.')[1]
    payload = decrypt(payload)
    return payload


def get_username(token):
    payload = get_payload(token)
    return payload['username']


def check_token(token):
    username = get_username(token)
    last_token = cache.get(username)
    if last_token:
        return last_token == token
    return False
