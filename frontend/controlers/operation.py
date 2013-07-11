#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 Ruoyan Wong(@saipanno).
#
#                    Created at 2013/01/16.
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


import time
import json
from sqlalchemy import exc, desc
from flask.ext.login import login_required, current_user
from flask import render_template, request, redirect, url_for, flash, Blueprint

from frontend.forms.operation import CreatePingDetectForm, CreateSshDetectForm, CreatePreDefinedExecuteForm, \
    CreateCustomExecuteForm

from frontend.models.member import User
from frontend.models.operation import OperationDb

from frontend.extensions.database import db
from frontend.extensions.utility import format_address_list
from frontend.extensions.utility import format_template_vars


operation = Blueprint('operation', __name__, url_prefix='/operation')


@operation.route('/<kind>/list')
@login_required
def list_operation_ctrl(kind):

    executes = OperationDb.query.filter_by(kind=kind).order_by(desc(OperationDb.id)).all()

    for execute in executes:
        user = User.query.filter_by(id=int(execute.author)).first()
        execute.author = user.name

    return render_template('operation/list_operation.html', executes=executes, kind=kind)


@operation.route('/<int:operation_id>/show')
@login_required
def show_operation_ctrl(operation_id):

    default_next_page = request.values.get('next', url_for('user.index_ctrl'))

    try:
        execute = OperationDb.query.filter_by(id=operation_id).first()

    except exc.SQLAlchemyError:
        flash(u'Internal database error', 'error')
        return redirect(default_next_page)

    if execute is None:
        flash(u'The operating does not exist.', 'error')
        return redirect(default_next_page)

    elif execute.result == u'':
        flash(u'Operation has not completed', 'info')
        return redirect(url_for('operation.list_operation_ctrl', kind=execute.kind))

    fruits = json.loads(execute.result)
    return render_template('operation/show_operation.html', execute=execute, fruits=fruits)


@operation.route('/Ssh/create', methods=("GET", "POST"))
@login_required
def create_ssh_detect_ctrl():

    kind = u'Ssh'

    form = CreateSshDetectForm()

    if request.method == 'GET':

        return  render_template('operation/create_ssh_detect.html', form=form)

    elif request.method == 'POST':

        author = current_user.id
        datetime = time.strftime('%Y-%m-%d %H:%M')

        fruit = format_address_list(form.server_list.data)
        if fruit['status'] is not True:
            flash(fruit['desc'], 'error')
            return redirect(url_for('operation.create_ssh_detect_ctrl'))

        if form.ssh_config.data.id is None:
            flash(u'Ssh configuration is not selected', 'error')
            return redirect(url_for('operation.create_ssh_detect_ctrl'))

        operation = OperationDb(author, datetime, kind, fruit['servers'], u'', u'', form.ssh_config.data.id, 0, u'')
        db.session.add(operation)
        db.session.commit()

        flash(u'Creating an operation successful', 'success')
        return redirect(url_for('operation.list_operation_ctrl', kind=kind))


@operation.route('/Ping/create', methods=("GET", "POST"))
@login_required
def create_ping_detect_ctrl():

    kind = u'Ping'

    form = CreatePingDetectForm()

    if request.method == 'GET':

        return render_template('operation/create_ping_detect.html', form=form)

    elif request.method == 'POST':

        author = current_user.id
        datetime = time.strftime('%Y-%m-%d %H:%M')

        fruit = format_address_list(form.server_list.data)
        if fruit['status'] is not True:
            flash(fruit['desc'], 'error')
            return redirect(url_for('operation.create_ping_detect_ctrl'))

        operation = OperationDb(author, datetime, kind, fruit['servers'], u'', u'', 0, 0, u'')
        db.session.add(operation)
        db.session.commit()

        flash(u'Creating an operation successful', 'success')
        return redirect(url_for('operation.list_operation_ctrl', kind=kind))


@operation.route('/Custom/create', methods=("GET", "POST"))
@login_required
def create_custom_execute_ctrl():

    kind = u'Custom'

    form = CreateCustomExecuteForm()

    if request.method == 'GET':

        return  render_template('operation/create_custom_execute.html', form=form)

    elif request.method == 'POST':

        author = current_user.id
        datetime = time.strftime('%Y-%m-%d %H:%M')

        fruit = format_address_list(form.server_list.data)
        if fruit['status'] is not True:
            flash(fruit['desc'], 'error')
            return redirect(url_for('operation.create_custom_execute_ctrl'))

        if form.script_template == u'':
            flash(u'Script template can\'t be empty', 'error')
            return redirect(url_for('operation.create_custom_execute_ctrl'))

        if form.ssh_config.data.id is None:
            flash(u'Ssh configuration is not selected', 'error')
            return redirect(url_for('operation.create_custom_execute_ctrl'))

        template_vars_dict = format_template_vars(form.template_vars.data)
        if template_vars_dict['status'] is not True:
            flash(template_vars_dict['desc'], 'error')
            return redirect(url_for('operation.create_custom_execute_ctrl'))
        template_vars = json.dumps(template_vars_dict['vars'], ensure_ascii=False)

        operation = OperationDb(author, datetime, kind, fruit['servers'], form.script_template.data,
                                template_vars, form.ssh_config.data.id, 0, u'')
        db.session.add(operation)
        db.session.commit()

        flash(u'Creating an operation successful', 'success')
        return redirect(url_for('operation.list_operation_ctrl', kind=kind))


@operation.route('/PreDefined/create', methods=("GET", "POST"))
@login_required
def create_predefined_execute_ctrl():

    kind = u'PreDefined'

    form = CreatePreDefinedExecuteForm()

    if request.method == 'GET':

        return  render_template('operation/create_predefined_execute.html', form=form)

    elif request.method == 'POST':

        author = current_user.id
        datetime = time.strftime('%Y-%m-%d %H:%M')

        fruit = format_address_list(form.server_list.data)
        if fruit['status'] is not True:
            flash(fruit['desc'], 'error')
            return redirect(url_for('operation.create_predefined_execute_ctrl'))

        if form.script_template.data.id is None:
            flash(u'PreDefined script is not selected', 'error')
            return redirect(url_for('operation.create_predefined_execute_ctrl'))

        if form.ssh_config.data.id is None:
            flash(u'Ssh configuration is not selected', 'error')
            return redirect(url_for('operation.create_predefined_execute_ctrl'))

        template_vars_dict = format_template_vars(form.template_vars.data)
        if template_vars_dict['status'] is not True:
            flash(template_vars_dict['desc'], 'error')
            return redirect(url_for('operation.create_predefined_execute_ctrl'))
        template_vars = json.dumps(template_vars_dict['vars'], ensure_ascii=False)

        operation = OperationDb(author, datetime, kind, fruit['servers'], form.script_template.data.id,
                                template_vars, form.ssh_config.data.id, 0, u'')
        db.session.add(operation)
        db.session.commit()

        flash(u'Creating an operation successful', 'success')
        return redirect(url_for('operation.list_operation_ctrl', kind=kind))