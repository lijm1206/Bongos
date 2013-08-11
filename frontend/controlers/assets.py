#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 Ruoyan Wong(@saipanno).
#
#                    Created at 2013/08/04.
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


from flask import render_template, request, redirect, url_for, flash, Blueprint
from flask.ext.login import login_required

from frontend.models.account import Group
from frontend.models.assets import Server, IDC

from frontend.forms.assets import ServerForm

from frontend.extensions.database import db
from frontend.extensions.principal import UserAccessPermission


assets = Blueprint('assets', __name__, url_prefix='/assets')


@assets.route('/server/list')
@login_required
def list_server_ctrl():

    access = UserAccessPermission('assets.list_server_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    servers = Server.query.all()

    for server in servers:
        group_name = ''
        for group_id in server.groups.split(','):
            group = Group.query.filter_by(id=int(group_id)).first()
            group_name = '%s, %s' % (group_name, group.desc)
        server.group_name = group_name[2:]

        idc = IDC.query.filter_by(id=server.id).first()
        server.idc_name = idc.name

    return render_template('assets/server.html', servers=servers, type='list')


@assets.route('/server/<int:server_id>/edit', methods=("GET", "POST"))
@login_required
def edit_server_ctrl(server_id):

    access = UserAccessPermission('assets.edit_server_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    server = Server.query.filter_by(id=server_id).first()

    form = ServerForm(id=server.id, serial_number=server.serial_number, assets_number=server.assets_number,
                      desc=server.desc, ext_address=server.ext_address, int_address=server.int_address,
                      ipmi_address=server.ipmi_address, other_address=server.other_address, idc=server.idc,
                      rack=server.rack, manufacturer=server.manufacturer, model=server.model, cpu_info=server.cpu_info,
                      disk_info=server.disk_info, memory_info=server.memory_info)

    if request.method == 'POST' and form.validate():

        if form.serial_number.data != server.serial_number:
            server.serial_number = form.serial_number.data

        if form.assets_number.data != server.assets_number:
            server.assets_number = form.assets_number.data

        groups = list()
        for group in form.groups.data:
            groups.append(str(group.id))
        groups.sort()
        server_groups = ','.join(groups)
        if server_groups != server.groups:
            server.groups = server_groups

        if form.desc.data != server.desc:
            server.desc = form.desc.data

        if form.ext_address.data != server.ext_address:
            server.ext_address = form.ext_address.data

        if form.int_address != server.int_address:
            server.int_address = form.int_address.data

        if form.ipmi_address != server.ipmi_address:
            server.ipmi_address = form.ipmi_address.data

        if form.other_address != server.other_address:
            server.other_address = form.other_address.data

        if form.idc.data.id != server.idc:
            server.idc = form.idc.data.id

        if form.rack.data != server.rack:
            server.rack = form.rack.data

        if form.manufacturer.data != server.manufacturer:
            server.manufacturer = form.manufacturer.data

        if form.model.data != server.model:
            server.model = form.model.data

        if form.cpu_info.data != server.cpu_info:
            server.cpu_info = form.cpu_info.data

        if form.disk_info.data != server.disk_info:
            server.disk_info = form.disk_info.data

        if form.memory_info.data != server.memory_info:
            server.memory_info = form.memory_info.data

        db.session.commit()

        flash(u'Edit server successfully', 'success')
        return redirect(url_for('assets.list_server_ctrl'))

    else:
        return render_template('assets/server.html', form=form, type='edit')


@assets.route('/idc/list')
@login_required
def list_idc_ctrl():

    access = UserAccessPermission('assets.list_idc_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    idcs = IDC.query.all()

    return render_template('assets/idc.html', idcs=idcs, type='list')