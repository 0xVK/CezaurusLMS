from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
import re


def forbidden_username_validator(value):

    forbidden_usernames = ['admin', 'my_communities', 'communities', 'people', 'signup', 'logout', 'search',
                           'friends', 'settings', 'feed', 'loh']

    if value.lower() in forbidden_usernames:
        raise ValidationError(_('Це зарезервоване слово'))


def unique_username_ignore_case_validator(value):
    if User.objects.filter(username__iexact=value).exists():
        raise ValidationError(_('Логін занятий'))


def correct_format_validator(value):

    username_validator_regexp = '^[a-zA-Z][a-zA-Z0-9-_]{3,20}$'

    if not re.match(username_validator_regexp, value):
        raise ValidationError(_('Недопустимий формат'))
