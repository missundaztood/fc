# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, session, redirect, request, \
    url_for, g
from fcsite.models import schedules as scheds
from fcsite.models import notices
from fcsite.models import joins
from fcsite.utils import error_message, info_message, check_required, \
        check_in, do_validate
from fcsite.auth import do_login

mod = Blueprint('general', __name__)


def validate_join_request():
    validators = {}
    validators['name'] = [check_required]
    validators['home'] = [check_required]
    validators['email'] = [check_required]
    validators['sex'] = [check_required, check_in(u'男性', u'女性')]
    validators['age'] = [check_required, check_in('18-20', '21-23', '24-26',
        '27-29', '30-32', '33-35', '36-38', '39-41', '42-')]
    validators['car'] = [check_required, check_in(u'あり', u'なし')]
    validators['has_racket'] = [check_required, check_in(u'あり', u'なし')]
    validators['holiday'] = [check_required, check_in(u'土日', u'日',
        u'不定期')]
    validators['experience'] = [check_required, check_in(u'1 年未満',
        u'2 年未満', u'中級', u'中上級', u'上級')]
    validators['comment'] = [check_required]
    do_validate(request.form, validators)


@mod.route('/')
def index():
    info_msgs = []

    if g.user:
        ns = notices.find_showing()
        info_msgs = info_msgs + [notice_to_message(n) for n in ns]

    if g.user and scheds.has_non_registered_practice(g.user['id']):
        info_msgs.append(u'通知:未登録の練習があります。登録は' +
                u'<a href="%s">コチラから</a>。' % url_for('schedule.schedule'))
    return render_template('index.html', info_msgs=info_msgs)


def notice_to_message(notice):
    return u'%s:%s' % (notice['title'], notice['body'])


@mod.route('/login', methods=['POST'])
def login():
    passwd = request.form['password']
    if not do_login(passwd):
        error_message(u'ログインできません。パスワードが間違っています。')
    return redirect(url_for('general.index'))


@mod.route('/logout')
def logout():
    session.pop('user_id')
    return redirect(url_for('general.index'))


@mod.route('/report')
def report():
    return redirect(url_for('general.index'))


@mod.route('/gallery')
def gallery():
    return redirect(url_for('general.index'))


@mod.route('/join', methods=['GET', 'POST'])
def join():
    if request.method == 'GET':
        return render_template('join.html')

    try:
        validate_join_request()
    except ValueError, e:
        return render_template('join.html', errors=e.errors)

    name = request.form['name']
    home = request.form['home']
    email = request.form['email']
    sex = request.form['sex']
    age = request.form['age']
    car = request.form['car']
    has_racket = request.form['has_racket']
    holiday = request.form['holiday']
    experience = request.form['experience']
    comment = request.form['comment']
    joins.insert(name, home, email, sex, age, car, has_racket, holiday,
            experience, comment)

    info_message(message=u'後日、サークルのものから折り返し連絡します。',
            title=u'応募ありがとうございます！')
    return redirect(url_for('general.index'))
