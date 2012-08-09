# -*- coding: utf-8 -*-

from flask import g, flash, redirect, url_for, abort
from fcsite.models import users
from functools import wraps
import time


#############
# DECORATORS
#############

def requires_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            abort(401)
        return f(*args, **kwargs)
    return decorated_function


def requires_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not users.is_admin(g.user):
            abort(403)
        return f(*args, **kwargs)
    return requires_login(decorated_function)


def requires_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not users.has_permission(g.user, permission):
                abort(403)
            return f(*args, **kwargs)
        return requires_login(decorated_function)
    return decorator


#############
# VALIDATIONS
#############

def do_validate(form, validations):
    errors = {}

    for name in validations:
        input_value = form[name]
        try:
            [check(input_value) for check in validations[name]]
        except ValueError, e:
            errors[name] = e.message

    if errors:
        e = ValueError()
        e.errors = errors
        raise e


def check_date(s):
    if not s:
        return s
    try:
        time.strptime(s, '%Y-%m-%d')
    except ValueError:
        raise ValueError('日付形式ではありません')
    return s


def check_time(s):
    if not s:
        return s
    try:
        time.strptime(s, '%H:%M')
    except ValueError:
        raise ValueError('時刻形式ではありません')
    return s


def check_number(s):
    if not s:
        return s
    if not s.isdigit():
        raise ValueError('数値にしてください')
    return s


def check_required(s):
    if not s:
        raise ValueError('入力してください')
    return s


def check_in(*options):
    def checker(s):
        if s not in options:
            raise ValueError('不正な値です')
        return s
    return checker


#############
# UTILITIES
#############

def longzip(l1, l2):
    ret = []
    len1 = len(l1)
    len2 = len(l2)
    length = max(len1, len2)
    for i in xrange(length):
        pair = (l1[i] if i < len1 else None,
                l2[i] if i < len2 else None)
        ret.append(pair)
    return ret


#############
# FILTERS
#############

def format_datetime(dt):
    return dt.strftime('%m-%d(%a) %H:%M').decode('utf8')


def format_date(dt):
    return dt.strftime('%m-%d(%a)').decode('utf8')


def format_time(dt):
    return dt.strftime('%H:%M').decode('utf8')
