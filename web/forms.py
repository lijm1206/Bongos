#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    forms.py, in Briseis.
#
#
#    Created at 2013/01/16. Ruoyan Wong(@saipanno).


from flask.ext.wtf import Form, TextField, TextAreaField, HiddenField, SubmitField, SelectField, PasswordField


class UserLoginForm(Form):

    next = HiddenField()
    username = TextField(u'username', id='text')
    password = PasswordField(u'password', id='password')

    submit = SubmitField(u'login', id='submit', description='submit')

class CreateDefaultOperateForm(Form):

    select_choices = [(1, u'CDN User Initialize'), (2, u'CDN CentOS Initialize'), (3, u'CDN DNS Update'), (4, u'Server Reboot'), (5, u'Server Shutdown')]

    next = HiddenField()
    server = TextAreaField(u'address/hostname:', id='textarea', description=u'server you want to operated, support address or hostname.')
    script = SelectField(u'script', id='select', choices=select_choices, description=u'select script from given list.')

    submit = SubmitField(u'Create', id='submit', description='submit')

class CreateCustomOperateForm(Form):

    next = HiddenField()
    server = TextAreaField(u'address/hostname', id='textarea', description=u'server you want to operated, support address or hostname.')
    script = TextAreaField(u'script', id='textarea', description=u'select script from given list.')
    var = TextAreaField(u'var', id='textarea', description=u'var list.')

    submit = SubmitField(u'Create', id='submit', description='submit')