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


from sqlalchemy import exc, desc
from flask.ext.sqlalchemy import Pagination
from flask.ext.login import login_required, current_user
from flask import render_template, request, redirect, url_for, flash, Blueprint, json, Response, current_app

from frontend.forms.operation import CreatePingDetectForm, CreateSshDetectForm, CreateFabfileExecuteForm, \
    CreateCustomExecuteForm, CreatePowerCtrlForm

from frontend.models.operation import OperationDb
from frontend.models.dashboard import SshConfig, IpmiConfig, FabFile

from frontend.extensions.database import db
from frontend.extensions.principal import AuthorizeRequired
from frontend.extensions.libs import format_address_list, format_ext_variables, get_obj_attributes, get_dict_items

from application import backend_runner
from frontend.extensions.tasks import q


operation = Blueprint('operation', __name__, url_prefix='/operation')
authorize_required = AuthorizeRequired('operation')


@operation.route('/list/', defaults={'page': 1})
@operation.route('/list/page/<int:page>')
@login_required
def list_operation_handler(page):

    pagination = OperationDb.query.order_by(desc(OperationDb.id)).paginate(page, 20)

    return render_template('operation/list_operation.html', operations=pagination.items, pagination=pagination)


@operation.route('/<int:operation_id>/show')
@login_required
@authorize_required
def show_operation_handler(operation_id):

    default_next_page = request.values.get('next', url_for('account.index_handler'))

    try:
        operation = OperationDb.query.filter_by(id=operation_id).first()

    except exc.SQLAlchemyError:
        flash(u'Internal database error', 'error')
        return redirect(default_next_page)

    if operation is None:
        flash(u'The operating does not exist.', 'error')
        return redirect(default_next_page)

    try:
        fruits = json.loads(operation.result)
    except ValueError:
        fruits = dict()

    return render_template('operation/show_operation.html', operation=operation, fruits=fruits)


@operation.route('/<int:operation_id>/export.csv')
@login_required
@authorize_required
def export_operation_handler(operation_id):

    try:
        execute = OperationDb.query.filter_by(id=operation_id).first()

    except exc.SQLAlchemyError:
        flash(u'Internal database error', 'error')
        return redirect(url_for('operation.list_operation_handler'))

    try:
        fruits = json.loads(execute.result)
    except ValueError:
        fruits = dict()

    # Each yield expression is directly sent to the browser
    def create_result_csv():
        yield 'address,return code,message,error message\n'
        for address in fruits:
            yield '%s,%s,%s,%s\n' % \
                  (address, fruits[address].get('code', ''),
                   fruits[address].get('msg', ''), fruits[address].get('error', ''))

    return Response(create_result_csv(), mimetype='text/csv')


@operation.route('/ssh_status/create', methods=("GET", "POST"))
@login_required
@authorize_required
def create_ssh_status_detecting_handler():

    operation_type = u'ssh_status_detecting'

    form = CreateSshDetectForm()

    if form.validate_on_submit():

        author = current_user.id

        fruit = format_address_list(form.server_list.data)
        if fruit['status'] is not True:
            flash(fruit['desc'], 'error')
            return redirect(url_for('operation.create_ssh_status_detecting_handler'))

        operation = OperationDb(author, operation_type, fruit['servers'], u'', u'', form.ssh_config.data.id, 0, u'')
        db.session.add(operation)
        db.session.commit()

        ssh_config = SshConfig.query.filter_by(id=form.ssh_config.data.id).first()
        ssh_config_dict = get_obj_attributes(ssh_config, 'SSH')

        operations = get_obj_attributes(operation, 'OPT')
        operations.update(ssh_config_dict)

        q.enqueue(backend_runner, operations, get_dict_items(current_app.config, 'SETTINGS'))

        flash(u'Creating operation successfully', 'success')
        return redirect(url_for('operation.list_operation_handler'))

    else:
        return render_template('operation/create_ssh_detecting.html', form=form)


@operation.route('/ping_detecting/create', methods=("GET", "POST"))
@login_required
@authorize_required
def create_ping_connectivity_detecting_handler():

    operation_type = u'ping_connectivity_detecting'

    form = CreatePingDetectForm()

    if form.validate_on_submit():

        author = current_user.id

        fruit = format_address_list(form.server_list.data)
        if fruit['status'] is not True:
            flash(fruit['desc'], 'error')
            return redirect(url_for('operation.create_ping_connectivity_detecting_handler'))

        operation = OperationDb(author, operation_type, fruit['servers'], u'', u'', 0, 0, u'')
        db.session.add(operation)
        db.session.commit()

        q.enqueue(backend_runner, get_obj_attributes(operation, 'OPT'), get_dict_items(current_app.config, 'SETTINGS'))

        flash(u'Creating operation successfully', 'success')
        return redirect(url_for('operation.list_operation_handler'))

    else:
        return render_template('operation/create_ping_detecting.html', form=form)



@operation.route('/custom_execute/create', methods=("GET", "POST"))
@login_required
@authorize_required
def create_custom_execute_handler():

    operation_type = u'custom_script_execute'

    form = CreateCustomExecuteForm()

    if form.validate_on_submit():

        author = current_user.id

        fruit = format_address_list(form.server_list.data)
        if fruit['status'] is not True:
            flash(fruit['desc'], 'error')
            return redirect(url_for('operation.create_custom_execute_handler'))

        ext_variables_dict = format_ext_variables(form.ext_variables.data)
        if ext_variables_dict['status'] is not True:
            flash(ext_variables_dict['desc'], 'error')
            return redirect(url_for('operation.create_custom_execute_handler'))
        ext_variables = json.dumps(ext_variables_dict['vars'], ensure_ascii=False)

        operation = OperationDb(author, operation_type, fruit['servers'], form.script_template.data,
                                ext_variables, form.ssh_config.data.id, 0, u'')
        db.session.add(operation)
        db.session.commit()

        ssh_config = SshConfig.query.filter_by(id=form.ssh_config.data.id).first()
        ssh_config_dict = get_obj_attributes(ssh_config, 'SSH')

        operations = get_obj_attributes(operation, 'OPT')
        operations.update(ssh_config_dict)

        q.enqueue(backend_runner, operations, get_dict_items(current_app.config, 'SETTINGS'))

        flash(u'Creating operation successfully', 'success')
        return redirect(url_for('operation.list_operation_handler'))

    else:
        return render_template('operation/create_custom_execute.html', form=form)


@operation.route('/fabfile_execute/create', methods=("GET", "POST"))
@login_required
@authorize_required
def create_fabfile_execute_handler():

    operation_type = u'fabfile_execute'

    form = CreateFabfileExecuteForm()

    if form.validate_on_submit():

        author = current_user.id

        fruit = format_address_list(form.server_list.data)
        if fruit['status'] is not True:
            flash(fruit['desc'], 'error')
            return redirect(url_for('operation.create_fabfile_execute_handler'))

        ext_variables_dict = format_ext_variables(form.ext_variables.data)
        if ext_variables_dict['status'] is not True:
            flash(ext_variables_dict['desc'], 'error')
            return redirect(url_for('operation.create_fabfile_execute_handler'))
        ext_variables = json.dumps(ext_variables_dict['vars'], ensure_ascii=False)

        operation = OperationDb(author, operation_type, fruit['servers'], form.script_template.data.id,
                                ext_variables, form.ssh_config.data.id, 0, u'')
        db.session.add(operation)
        db.session.commit()

        ssh_config = SshConfig.query.filter_by(id=form.ssh_config.data.id).first()
        ssh_config_dict = get_obj_attributes(ssh_config, 'SSH')
        fabfile = FabFile.query.filter_by(id=form.script_template.data.id).first()
        fabfile_dict = get_obj_attributes(fabfile, 'FABFILE')

        operations = get_obj_attributes(operation, 'OPT')
        operations.update(ssh_config_dict)
        operations.update(fabfile_dict)

        q.enqueue(backend_runner, operations, get_dict_items(current_app.config, 'SETTINGS'))

        flash(u'Creating operation successfully', 'success')
        return redirect(url_for('operation.list_operation_handler'))

    else:
        return render_template('operation/create_fabfile_execute.html', form=form)


@operation.route('/remote_control/create', methods=("GET", "POST"))
@login_required
@authorize_required
def create_remote_control_handler():

    operation_type = u'remote_control'

    form = CreatePowerCtrlForm()

    if form.validate_on_submit():

        author = current_user.id

        fruit = format_address_list(form.server_list.data)
        if fruit['status'] is not True:
            flash(fruit['desc'], 'error')
            return redirect(url_for('operation.create_remote_control_handler'))

        operation = OperationDb(author, operation_type, fruit['servers'],
                                form.script_template.data, u'', form.ipmi_config.data.id, 0, u'')
        db.session.add(operation)
        db.session.commit()

        ipmi_config = IpmiConfig.query.filter_by(id=form.ipmi_config.data.id).first()
        ipmi_config_dict = get_obj_attributes(ipmi_config, 'IPMI')
        operations = get_obj_attributes(operation, 'OPT')
        operations.update(ipmi_config_dict)

        print operations

        q.enqueue(backend_runner, operations, get_dict_items(current_app.config, 'SETTINGS'))

        flash(u'Creating operation successfully', 'success')
        return redirect(url_for('operation.list_operation_handler'))

    else:
        return render_template('operation/create_power_control.html', form=form)