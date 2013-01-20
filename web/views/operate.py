#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    operate.py, in Briseis.
#
#
#    Created at 2013/01/16. Ruoyan Wong(@saipanno).

import time

from flask import render_template, request, redirect, url_for, flash, g
from sqlalchemy import desc

from web import db
from web import app

from web.forms import CreateDefaultOperateForm
from web.forms import CreateCustomOperateForm

from web.models import PreDefinedOperate
from web.models import CustomOperate
from web.models import PreDefinedScript
from web.models import SshConfig

@app.route('/operate/create', methods=("GET", "POST"))
@app.route('/operate/create/default', methods=("GET", "POST"))
def create_default_operate_ctrl():

    form = CreateDefaultOperateForm()

    if request.method == 'GET':

        return render_template('operate/operate_create_default.html', form=form)

    elif request.method == 'POST':

        operate = PreDefinedOperate(time.strftime('%Y-%m-%d %H:%M'), form.server.data, form.script_id.data, form.config.data)
        db.session.add(operate)
        db.session.commit()

        flash(u'Create operate successful.', 'success')

        return redirect(url_for('show_default_operate_ctrl'))

@app.route('/operate/create/custom', methods=("GET", "POST"))
def create_custom_operate_ctrl():

    form = CreateCustomOperateForm()

    if request.method == 'GET':

        return  render_template('operate/operate_create_custom.html', form=form)

    elif request.method == 'POST':

        operate = CustomOperate(time.strftime('%Y-%m-%d %H:%M'), form.server.data, form.template_script.data, form.template_vars.data, form.config.data)
        db.session.add(operate)
        db.session.commit()

        flash(u'Create operate successful.', 'success')

        return redirect(url_for('show_custom_operate_ctrl', status='success', message='Operate create successful.'))

@app.route('/operate/show')
@app.route('/operate/show/default')
def show_default_operate_ctrl():

    if request.method == 'GET':

        operates = PreDefinedOperate.query.order_by(desc(PreDefinedOperate.id)).all()

        return render_template('operate/operate_show_default.html', operates=operates)

@app.route('/operate/show/custom')
def show_custom_operate_ctrl():

    if request.method == 'GET':

        operates = CustomOperate.query.order_by(desc(CustomOperate.id)).all()

        return render_template('operate/operate_show_custom.html', operates=operates)