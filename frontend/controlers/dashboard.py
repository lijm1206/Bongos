#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 Ruoyan Wong(@saipanno).
#
#                    Created at 2013/01/23.
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


import os
import io
from flask import render_template, request, redirect, url_for, flash, Blueprint, current_app
from flask.ext.login import login_required, current_user

from frontend.extensions.database import db
from frontend.extensions.libs import catch_errors

from frontend.models.account import User, Group
from frontend.models.dashboard import SshConfig, IpmiConfig, Permission, FabFile
from frontend.models.assets import Server, IDC

from frontend.forms.assets import ServerForm, IDCForm
from frontend.forms.account import GroupForm
from frontend.forms.dashboard import SshConfigForm, IpmiConfigForm, CreateUserForm, EditUserForm, FabFileForm

from frontend.extensions.principal import UserAccessPermission


dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard.route('/logging')
@login_required
def show_logging_ctrl():

    access = UserAccessPermission('dashboard.show_logging_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    MAX_LEN = -20
    with open(current_app.config['LOGGING_FILENAME'], 'r') as f:
        logging_buffer = f.readlines()
        return render_template('dashboard/logging_reader.html', logging_buffer=logging_buffer[MAX_LEN:])


@dashboard.route('/user/list')
@login_required
def list_user_ctrl():

    access = UserAccessPermission('dashboard.list_user_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    users = User.query.all()

    for user in users:
        groups_name = ''
        for group_id in user.groups.split(','):
            group = Group.query.filter_by(id=int(group_id)).first()
            groups_name = '%s, %s' % (groups_name, group.desc)
        user.groups_name = groups_name[2:]

    return render_template('dashboard/user_manager.html', users=users, type='list')


@dashboard.route('/user/create', methods=("GET", "POST"))
@login_required
def create_user_ctrl():

    access = UserAccessPermission('dashboard.create_user_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    form = CreateUserForm()

    if request.method == 'POST' and form.validate():

        groups = list()
        for group in form.groups.data:
            groups.append(str(group.id))
        groups.sort()

        user = User(form.email.data, form.username.data, form.name.data,
                    ','.join(groups), form.password.data, 1 if form.status.data else 0)
        db.session.add(user)
        db.session.commit()

        flash(u'Creating user successfully', 'success')

        return redirect(url_for('dashboard.list_user_ctrl'))

    else:
        return render_template('dashboard/user_manager.html', form=form, type='create')


@dashboard.route('/user/<int:user_id>/edit', methods=("GET", "POST"))
@login_required
def edit_user_ctrl(user_id):

    access = UserAccessPermission('dashboard.edit_user_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    user = User.query.filter_by(id=user_id).first()

    form = EditUserForm(id=user.id, email=user.email, username=user.username, name=user.name,
                        status=True if user.status else False)

    if request.method == 'POST' and form.validate():

        if form.name.data != user.name:
            user.name = form.name.data

        if len(form.password.data) > 0:
            user.update_password(form.password.data)

        groups = list()
        for group in form.groups.data:
            groups.append(str(group.id))
        groups.sort()
        user_groups = ','.join(groups)

        if user_groups != user.groups:
            user.groups = user_groups

        if user.status or form.status.data:
            user.status = 1 if form.status.data else 0

        db.session.commit()
        flash(u'Update user settings successfully', 'success')

        return redirect(url_for('dashboard.list_user_ctrl'))

    else:
        return render_template('dashboard/user_manager.html', form=form, type='edit')


@dashboard.route('/user/<int:user_id>/status/<status>')
@login_required
def update_user_status_ctrl(user_id, status):

    access = UserAccessPermission('dashboard.update_user_status_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    user = User.query.filter_by(id=user_id).first()

    if status == 'disable':
        user.status = 0
        db.session.commit()

        flash(u'Disable user successfully', 'success')
    elif status == 'enable':
        user.status = 1
        db.session.commit()

        flash(u'Enable user successfully', 'success')
    elif status == 'delete':

        db.session.delete(user)
        db.session.commit()

        flash(u'Delete user successfully', 'success')

    else:
        flash(u'Incorrect user status format', 'error')

    return redirect(url_for('dashboard.list_user_ctrl'))


@dashboard.route('/ssh_config/list')
@login_required
def list_ssh_config_ctrl():

    access = UserAccessPermission('dashboard.list_ssh_config_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    ssh_configs = SshConfig.query.all()
    for ssh_config in ssh_configs:
        user = User.query.filter_by(id=ssh_config.author).first()
        ssh_config.author_name = user.name

        groups_name = ''
        for group_id in ssh_config.groups.split(','):
            group = Group.query.filter_by(id=int(group_id)).first()
            groups_name = '%s, %s' % (groups_name, group.desc)
        ssh_config.groups_name = groups_name[2:]

    return render_template('dashboard/ssh_config.html', ssh_configs=ssh_configs, type='list')


@dashboard.route('/ssh_config/create', methods=("GET", "POST"))
@login_required
def create_ssh_config_ctrl():

    access = UserAccessPermission('dashboard.create_ssh_config_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    form = SshConfigForm()

    if request.method == 'GET':
        return render_template('dashboard/ssh_config.html', form=form, type='create')

    elif request.method == 'POST' and form.validate():

        groups = list()
        for group in form.groups.data:
            groups.append(str(group.id))
        groups.sort()

        ssh_config = SshConfig(form.username.data, form.desc.data, current_user.id, ','.join(groups), form.port.data,
                               form.username.data, form.password.data, form.private_key.data)
        db.session.add(ssh_config)
        db.session.commit()

        flash(u'Creating ssh configuration successfully', 'success')

        return redirect(url_for('dashboard.list_ssh_config_ctrl'))

    else:
        messages = catch_errors(form.errors)

        flash(messages, 'error')
        return redirect(url_for('dashboard.create_ssh_config_ctrl'))


@dashboard.route('/ssh_config/<int:config_id>/edit', methods=("GET", "POST"))
@login_required
def edit_ssh_config_ctrl(config_id):

    access = UserAccessPermission('dashboard.edit_ssh_config_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    config = SshConfig.query.filter_by(id=config_id).first()

    form = SshConfigForm(id=config.id, name=config.name, desc=config.desc, port=config.port, username=config.username,
                         private_key=config.private_key)

    if request.method == 'GET':
        return render_template('dashboard/ssh_config.html', form=form, type='edit')

    elif request.method == 'POST' and form.validate():

        if form.name.data != config.name:
            config.name = form.name.data

        if form.desc.data != config.desc:
            config.desc = form.desc.data

        groups = list()
        for group in form.groups.data:
            groups.append(str(group.id))
        groups.sort()
        config_groups = ','.join(groups)

        if config_groups != config.groups:
            config.groups = config_groups

        if form.port.data != config.port:
            config.port = form.port.data

        if form.username.data != config.username:
            config.username = form.username.data

        if form.password.data != config.password:
            config.password = form.password.data

        if form.private_key.data != config.private_key:
            config.private_key = form.private_key.data

        db.session.commit()

        flash(u'Edit ssh configuration successfully', 'success')
        return redirect(url_for('dashboard.list_ssh_config_ctrl'))

    else:
        messages = catch_errors(form.errors)

        flash(messages, 'error')
        return redirect(url_for('dashboard.edit_ssh_config_ctrl', config_id=config_id))


@dashboard.route('/ssh_config/<int:config_id>/delete')
@login_required
def delete_ssh_config_ctrl(config_id):

    access = UserAccessPermission('dashboard.delete_ssh_config_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    config = SshConfig.query.filter_by(id=config_id).first()

    # TODO:增加清理数据库环境操作

    db.session.delete(config)
    db.session.commit()

    flash(u'Delete ssh configuration successfully', 'success')
    return redirect(url_for('dashboard.list_ssh_config_ctrl'))


@dashboard.route('/ipmi_config/list')
@login_required
def list_ipmi_config_ctrl():

    access = UserAccessPermission('dashboard.list_ipmi_config_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    ipmi_configs = IpmiConfig.query.all()
    for ipmi_config in ipmi_configs:
        user = User.query.filter_by(id=ipmi_config.author).first()
        ipmi_config.author_name = user.name

        groups_name = ''
        for group_id in ipmi_config.groups.split(','):
            group = Group.query.filter_by(id=int(group_id)).first()
            groups_name = '%s, %s' % (groups_name, group.desc)
        ipmi_config.groups_name = groups_name[2:]

    return render_template('dashboard/ipmi_config.html', ipmi_configs=ipmi_configs, type='list')


@dashboard.route('/ipmi_config/create', methods=("GET", "POST"))
@login_required
def create_ipmi_config_ctrl():

    access = UserAccessPermission('dashboard.create_ipmi_config_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    form = IpmiConfigForm()

    if request.method == 'GET':
        return render_template('dashboard/ipmi_config.html', form=form, type='create')

    elif request.method == 'POST' and form.validate():

        groups = list()
        for group in form.groups.data:
            groups.append(str(group.id))
        groups.sort()

        ipmi_config = IpmiConfig(form.username.data, form.desc.data, current_user.id, ','.join(groups),
                                 form.username.data, form.password.data, 1 if form.interface.data else 0)
        db.session.add(ipmi_config)
        db.session.commit()

        flash(u'Creating IPMI configuration successfully', 'success')

        return redirect(url_for('dashboard.list_ipmi_config_ctrl'))

    else:
        messages = catch_errors(form.errors)

        flash(messages, 'error')
        return redirect(url_for('dashboard.create_ipmi_config_ctrl'))


@dashboard.route('/ipmi_config/<int:config_id>/edit', methods=("GET", "POST"))
@login_required
def edit_ipmi_config_ctrl(config_id):

    access = UserAccessPermission('dashboard.edit_ipmi_config_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    config = IpmiConfig.query.filter_by(id=config_id).first()

    form = IpmiConfigForm(id=config.id, name=config.name, desc=config.desc, username=config.username,
                          interface=True if config.interface else False)

    if request.method == 'GET':
        return render_template('dashboard/ipmi_config.html', form=form, type='edit')

    elif request.method == 'POST' and form.validate():

        if form.name.data != config.name:
            config.name = form.name.data

        if form.desc.data != config.desc:
            config.desc = form.desc.data

        groups = list()
        for group in form.groups.data:
            groups.append(str(group.id))
        groups.sort()
        config_groups = ','.join(groups)

        if config_groups != config.groups:
            config.groups = config_groups

        if form.username.data != config.username:
            config.username = form.username.data

        if form.password.data != config.password:
            config.password = form.password.data

        if form.interface.data or config.interface:
            config.interface = 1 if form.interface.data else 0

        db.session.commit()

        flash(u'Edit IPMI configuration successfully', 'success')
        return redirect(url_for('dashboard.list_ipmi_config_ctrl'))

    else:
        messages = catch_errors(form.errors)

        flash(messages, 'error')
        return redirect(url_for('dashboard.edit_ipmi_config_ctrl', config_id=config_id))


@dashboard.route('/ipmi_config/<int:config_id>/delete')
@login_required
def delete_ipmi_config_ctrl(config_id):

    access = UserAccessPermission('dashboard.delete_ipmi_config_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    config = IpmiConfig.query.filter_by(id=config_id).first()

    # TODO:增加清理数据库环境操作

    db.session.delete(config)
    db.session.commit()

    flash(u'Delete IPMI configuration successfully', 'success')
    return redirect(url_for('dashboard.list_ipmi_config_ctrl'))


@dashboard.route('/group/list')
@login_required
def list_group_ctrl():

    access = UserAccessPermission('dashboard.list_group_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    group_members = dict()
    users = User.query.all()
    groups = Group.query.all()

    for group in groups:
        for user in users:
            if unicode(group.id) in user.groups.split(','):
                try:
                    group_members[unicode(group.id)] = '%s, %s' % (group_members[unicode(group.id)], user.name)
                except:
                    group_members[unicode(group.id)] = user.name

        group.members = group_members.get(unicode(group.id), u'')

    return render_template('dashboard/group_manager.html', groups=groups, type='list')


@dashboard.route('/group/create', methods=("GET", "POST"))
@login_required
def create_group_ctrl():

    access = UserAccessPermission('dashboard.create_group_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    form = GroupForm()

    if request.method == 'GET':

        return render_template('dashboard/group_manager.html', form=form, type='create')

    elif request.method == 'POST' and form.validate():

        group = Group(form.name.data, form.desc.data)
        db.session.add(group)
        db.session.commit()

        flash(u'Create group successfully', 'success')
        return redirect(url_for('dashboard.list_group_ctrl'))

    else:
        messages = catch_errors(form.errors)

        flash(messages, 'error')
        return redirect(url_for('dashboard.create_group_ctrl'))


@dashboard.route('/group/<int:group_id>/edit', methods=("GET", "POST"))
@login_required
def edit_group_ctrl(group_id):

    access = UserAccessPermission('dashboard.edit_group_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    group = Group.query.filter_by(id=group_id).first()

    form = GroupForm(id=group.id, name=group.name, desc=group.desc)

    if request.method == 'GET':

        return render_template('dashboard/group_manager.html', form=form, type='edit')

    elif request.method == 'POST' and form.validate():

        if form.name.data != group.name:
            group.name = form.name.data

        if form.desc.data != group.desc:
            group.desc = form.desc.data

        db.session.commit()

        flash(u'Edit group successfully', 'success')
        return redirect(url_for('dashboard.list_group_ctrl'))

    else:
        messages = catch_errors(form.errors)

        flash(messages, 'error')
        return redirect(url_for('dashboard.edit_group_ctrl', group_id=group_id))


@dashboard.route('/group/<int:group_id>/delete')
@login_required
def delete_group_ctrl(group_id):

    access = UserAccessPermission('dashboard.delete_group_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    group = Group.query.filter_by(id=group_id).first()

    # 清理用户的Group属性
    users = User.query.all()
    for user in users:
        if unicode(group.id) in user.groups.split(','):
            user_groups = user.groups.split(',')
            user_groups.remove(unicode(group.id))
            user_groups.sort()
            user.groups = ','.join(user_groups)

    # 清理权限的Group属性
    permissions = Permission.query.all()
    for permission in permissions:
        permission_rules = permission.rules.split(',')
        permission_rules.remove(unicode(group_id))
        permission_rules.sort()
        permission.rules = ','.join(permission_rules)

    db.session.delete(group)
    db.session.commit()

    flash(u'Edit group successfully', 'success')
    return redirect(url_for('dashboard.list_group_ctrl'))


@dashboard.route('/permission/show')
@login_required
def show_permission_ctrl():

    access = UserAccessPermission('dashboard.show_permission_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    user_groups = dict()
    group_permissions = dict()
    permissions_handler = list()

    groups = Group.query.all()
    for group in groups:
        user_groups[unicode(group.id)] = group.desc

    permissions = Permission.query.all()
    for permission in permissions:

        permission_id = permission.id
        permission_desc = permission.desc
        permissions_handler.append(dict(id=permission_id, desc=permission_desc))

        permission_rules = permission.rules.split(',')

        for group_id in permission_rules:

            try:
                group_permissions[group_id][permission_id] = 1
            except Exception:
                group_permissions[group_id] = dict()
                group_permissions[group_id][permission_id] = 1

    return render_template('dashboard/acl_manager.html', permissions_handler=permissions_handler,
                           user_groups=user_groups, group_permissions=group_permissions, type='show')


@dashboard.route('/permission/<group_id>/<handler_id>/status/<status>')
@login_required
def update_permission_ctrl(group_id, handler_id, status):

    access = UserAccessPermission('dashboard.update_permission_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    permission = Permission.query.filter_by(id=handler_id).first()

    permission_rules = permission.rules.split(',')

    if status == 'disable':
        permission_rules.remove(unicode(group_id))
    elif status == 'enable':
        permission_rules.append(unicode(group_id))
    else:
        flash(u'Error permission status', 'error')
        return redirect(url_for('dashboard.show_permission_ctrl'))

    permission_rules.sort()
    permission.rules = ','.join(permission_rules)
    db.session.commit()

    flash(u'Update permission successfully', 'success')
    return redirect(url_for('dashboard.show_permission_ctrl'))


@dashboard.route('/fabfile/list')
@login_required
def list_fabfile_ctrl():

    access = UserAccessPermission('dashboard.list_fabfile_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    fabfiles = FabFile.query.all()

    for fabfile in fabfiles:
        user = User.query.filter_by(id=int(fabfile.author)).first()
        fabfile.author_name = user.name

        groups_name = ''
        for group_id in fabfile.groups.split(','):
            group = Group.query.filter_by(id=int(group_id)).first()
            groups_name = '%s, %s' % (groups_name, group.desc)
        fabfile.groups_name = groups_name[2:]

    return render_template('dashboard/fabfile_manager.html', fabfiles=fabfiles, type='list')


@dashboard.route('/fabfile/<int:fabfile_id>/show')
@login_required
def show_fabfile_ctrl(fabfile_id):

    access = UserAccessPermission('dashboard.show_fabfile_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    default_next_page = request.values.get('next', url_for('account.index_ctrl'))

    fabfile = FabFile.query.filter_by(id=fabfile_id).first()

    if fabfile is None:
        flash(u'Fabfile does not exist', 'error')
        return redirect(default_next_page)

    with io.open(os.path.join(current_app.config['FABRIC_FILE_PATH'], '%s.py' % fabfile.name), mode='rt',
                 encoding='utf-8') as f:
        fabfile.script = f.read()

    return render_template('dashboard/fabfile_manager.html', fabfile=fabfile, type='show')


@dashboard.route('/fabfile/create', methods=("GET", "POST"))
@login_required
def create_fabfile_ctrl():

    access = UserAccessPermission('dashboard.create_fabfile_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    form = FabFileForm()
    if request.method == 'GET':
        return render_template('dashboard/fabfile_manager.html', form=form, type='create')

    elif request.method == 'POST' and form.validate():

        groups = list()
        for group in form.groups.data:
            groups.append(str(group.id))
        groups.sort()

        with io.open(os.path.join(current_app.config['FABRIC_FILE_PATH'], '%s.py' % form.name.data), mode='wt',
                    encoding='utf-8') as f:
            f.write(form.script.data.replace('\r\n', '\n').replace('\r', '\n'))

        fabfile = FabFile(form.name.data, form.desc.data, current_user.id, ','.join(groups))
        db.session.add(fabfile)
        db.session.commit()

        flash(u'Create fabfile successfully', 'success')
        return redirect(url_for('dashboard.list_fabfile_ctrl'))

    else:
        messages = catch_errors(form.errors)

        flash(messages, 'error')
        return redirect(url_for('dashboard.create_fabfile_ctrl'))


@dashboard.route('/fabfile/<int:fabfile_id>/edit', methods=("GET", "POST"))
@login_required
def edit_fabfile_ctrl(fabfile_id):

    access = UserAccessPermission('dashboard.edit_fabfile_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    fabfile = FabFile.query.filter_by(id=fabfile_id).first()
    with io.open(os.path.join(current_app.config['FABRIC_FILE_PATH'], '%s.py' % fabfile.name), mode='rt',
                 encoding='utf-8') as f:
        fabfile.script = f.read()

    form = FabFileForm(id=fabfile.id, name=fabfile.name, desc=fabfile.desc, script=fabfile.script)

    if request.method == 'GET':
        return render_template('dashboard/fabfile_manager.html', form=form, type='edit')

    elif request.method == 'POST' and form.validate():

        with io.open(os.path.join(current_app.config['FABRIC_FILE_PATH'], '%s.py' % form.name.data), mode='wt',
                  encoding='utf-8') as f:
            f.write(form.script.data.replace('\r\n', '\n').replace('\r', '\n'))

        if form.desc.data != fabfile.desc:
            fabfile.desc = form.desc.data

        groups = list()
        for group in form.groups.data:
            groups.append(str(group.id))
        groups.sort()
        config_groups = ','.join(groups)

        if config_groups != fabfile.groups:
            fabfile.groups = config_groups

        db.session.commit()

        flash(u'Edit fabfile successfully', 'success')
        return redirect(url_for('dashboard.list_fabfile_ctrl'))

    else:
        messages = catch_errors(form.errors)

        flash(messages, 'error')
        return redirect(url_for('dashboard.create_fabfile_ctrl'))


@dashboard.route('/fabfile/<int:fabfile_id>/delete')
@login_required
def delete_fabfile_ctrl(fabfile_id):

    access = UserAccessPermission('dashboard.delete_fabfile_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    fabfile = FabFile.query.filter_by(id=fabfile_id).first()

    # TODO:增加清理数据库环境操作

    db.session.delete(fabfile)
    db.session.commit()

    flash(u'Edit idc successfully', 'success')
    return redirect(url_for('dashboard.list_fabfile_ctrl'))


@dashboard.route('/server/list')
@login_required
def list_server_ctrl():

    access = UserAccessPermission('dashboard.list_server_ctrl')
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

    return render_template('dashboard/server_manager.html', servers=servers, type='list')


@dashboard.route('/server/create', methods=("GET", "POST"))
@login_required
def create_server_ctrl():

    access = UserAccessPermission('dashboard.create_server_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    form = ServerForm()

    if request.method == 'GET':

        return render_template('dashboard/server_manager.html', form=form, type='create')

    elif request.method == 'POST' and form.validate():

        groups = list()
        for group in form.groups.data:
            groups.append(str(group.id))
        groups.sort()

        server = Server(form.serial_number.data, form.assets_number.data, groups,
                        form.desc.data, form.ext_address.data, form.int_address.data, form.ipmi_address.data,
                        form.other_address.data, form.idc.data.id, form.rack.data, form.manufacturer.data,
                        form.model.data, form.cpu_info.data, form.disk_info.data, form.memory_info.data)
        db.session.add(server)
        db.session.commit()

        flash(u'Create server successfully', 'success')
        return redirect(url_for('dashboard.list_server_ctrl'))

    else:
        messages = catch_errors(form.errors)

        flash(messages, 'error')
        return redirect(url_for('dashboard.create_server_ctrl'))


@dashboard.route('/server/<int:server_id>/edit', methods=("GET", "POST"))
@login_required
def edit_server_ctrl(server_id):

    access = UserAccessPermission('dashboard.edit_server_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    server = Server.query.filter_by(id=server_id).first()

    form = ServerForm(id=server.id, serial_number=server.serial_number, assets_number=server.assets_number,
                      desc=server.desc, ext_address=server.ext_address, int_address=server.int_address,
                      ipmi_address=server.ipmi_address, other_address=server.other_address, idc=server.idc,
                      rack=server.rack, manufacturer=server.manufacturer, model=server.model, cpu_info=server.cpu_info,
                      disk_info=server.disk_info, memory_info=server.memory_info)

    if request.method == 'GET':

        return render_template('dashboard/server_manager.html', form=form, type='edit')

    elif request.method == 'POST' and form.validate():

        if form.serial_number.data != server.serial_number:
            server.serial_number = form.serial_number.data

        if form.assets_number.data != server.dashboard_number:
            server.dashboard_number = form.assets_number.data

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
        return redirect(url_for('dashboard.list_server_ctrl'))

    else:
        messages = catch_errors(form.errors)

        flash(messages, 'error')
        return redirect(url_for('dashboard.edit_server_ctrl', server_id=server_id))


@dashboard.route('/group/<int:server_id>/delete')
@login_required
def delete_server_ctrl(server_id):

    access = UserAccessPermission('dashboard.delete_server_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    server = Server.query.filter_by(id=server_id).first()

    db.session.delete(server)
    db.session.commit()

    flash(u'Edit server successfully', 'success')
    return redirect(url_for('dashboard.list_server_ctrl'))


@dashboard.route('/idc/list')
@login_required
def list_idc_ctrl():

    access = UserAccessPermission('dashboard.list_idc_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    idcs = IDC.query.all()

    return render_template('dashboard/idc_manager.html', idcs=idcs, type='list')


@dashboard.route('/idc/create', methods=("GET", "POST"))
@login_required
def create_idc_ctrl():

    access = UserAccessPermission('dashboard.create_idc_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    form = IDCForm()

    if request.method == 'GET':

        return render_template('dashboard/idc_manager.html', form=form, type='create')

    elif request.method == 'POST' and form.validate():

        group = IDC(form.name.data, form.desc.data, form.operators.data, form.address.data)
        db.session.add(group)
        db.session.commit()

        flash(u'Create IDC successfully', 'success')
        return redirect(url_for('dashboard.list_idc_ctrl'))

    else:
        messages = catch_errors(form.errors)

        flash(messages, 'error')
        return redirect(url_for('dashboard.create_idc_ctrl'))


@dashboard.route('/idc/<int:idc_id>/edit', methods=("GET", "POST"))
@login_required
def edit_idc_ctrl(idc_id):

    access = UserAccessPermission('dashboard.edit_idc_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    idc = IDC.query.filter_by(id=idc_id).first()

    form = IDCForm(id=idc.id, name=idc.name, desc=idc.desc, operators=idc.operators, address=idc.address)

    if request.method == 'GET':

        return render_template('dashboard/idc_manager.html', form=form, type='edit')

    elif request.method == 'POST' and form.validate():

        if form.name.data != idc.name:
            idc.name = form.name.data

        if form.operators.data != idc.operators:
            idc.operators = form.operators.data

        if form.address.data != idc.address:
            idc.address = form.address.data

        db.session.commit()

        flash(u'Edit IDC successfully', 'success')
        return redirect(url_for('dashboard.list_idc_ctrl'))

    else:
        messages = catch_errors(form.errors)

        flash(messages, 'error')
        return redirect(url_for('dashboard.edit_idc_ctrl', idc_id=idc_id))


@dashboard.route('/group/<int:idc_id>/delete')
@login_required
def delete_idc_ctrl(idc_id):

    access = UserAccessPermission('dashboard.delete_idc_ctrl')
    if not access.can():
        flash(u'Don\'t have permission to this page', 'warning')
        return redirect(url_for('account.index_ctrl'))

    idc = IDC.query.filter_by(id=idc_id).first()

    # TODO:增加清理数据库环境操作

    db.session.delete(idc)
    db.session.commit()

    flash(u'Edit idc successfully', 'success')
    return redirect(url_for('dashboard.list_idc_ctrl'))