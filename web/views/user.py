#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 Ruoyan Wong(@saipanno).
#
#                    Created at 2013/01/17.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from werkzeug.security import check_password_hash
from flask import render_template, request, flash, redirect, url_for, session

from web import app

from web.forms.user import UserLoginForm

from web.models.user import User

from web.extensions import login_required


@app.route('/', methods=['GET', 'POST'])
@login_required
def index_ctrl():

    return  redirect(url_for('show_operate_ctrl', operate_type='Ping'))


@app.route('/login', methods=['GET', 'POST'])
def user_login_ctrl():

    form = UserLoginForm()
    next_page = request.values.get('next', url_for('index_ctrl'))

    if request.method == 'GET':

        return  render_template('login.html', form=form)

    elif request.method == 'POST':

        if form.username.data == u'' or form.password.data == u'':

            flash(u'错误的用户名或密码.', 'error')
            return redirect(url_for('user_login_ctrl'))

        if session.get('is_login'):

            flash(u'已经登录.', 'success')
            return redirect(next_page)

        user = User.query.filter_by(username=form.username.data).first()

        if user is not None and check_password_hash(user.password, form.password.data):

            session['is_login'] = True
            session['user'] = user
            flash(u'登录成功.', 'success')
            return redirect(next_page)

        else:

            flash(u'错误的用户名或密码.', 'error')
            return redirect(url_for('user_login_ctrl'))


@app.route('/logout', methods=['GET'])
def user_logout_ctrl():

    session.pop('is_login', None)

    return redirect(url_for('index_ctrl'))