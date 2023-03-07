import pytz
from app.gamification.models.survey_template import SurveyTemplate
from app.gamification.models.feedback_survey import FeedbackSurvey
from app.gamification.models.artifact_review import ArtifactReview
from datetime import datetime

from django.forms.fields import DateTimeFormatsIterator
import time
import jwt
import os
from django.core import signing
import hashlib
from django.core.cache import cache


def get_user_pk(request):
    token = request.META.get('HTTP_AUTHORIZATION').split()[1]
    token_data = jwt.decode(token, os.getenv('SECRET_KEY'), algorithm='HS256')
    return token_data['id']


def parse_datetime(value):
    for format in DateTimeFormatsIterator():
        try:
            return datetime.strptime(value, format)
        except (ValueError, TypeError):
            pass
    raise ValueError('Invalid datetime string')


HEADER = {'typ': 'JWP', 'alg': 'default'}
KEY = 'GAMIFICATION'
SALT = 'gamification_platform'
TIME_OUT = 30 * 60  # 30min


def encrypt(obj):
    value = signing.dumps(obj, key=KEY, salt=SALT)
    value = signing.b64_encode(value.encode()).decode()
    return value


def decrypt(src):
    src = signing.b64_decode(src.encode()).decode()
    raw = signing.loads(src, key=KEY, salt=SALT)
    print(type(raw))
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


def check_survey_status(assignment):
    try:
        feedback_survey = FeedbackSurvey.objects.get(assignment=assignment)
    except FeedbackSurvey.DoesNotExist:
        return "feedback_survey_not_exist"
    due_date = feedback_survey.date_due.astimezone(
        pytz.timezone('America/Los_Angeles'))
    now = datetime.now().astimezone(pytz.timezone('America/Los_Angeles'))
    if due_date < now:
        return ArtifactReview.ArtifactReviewType.LATE
    else:
        return ArtifactReview.ArtifactReviewType.COMPLETED
