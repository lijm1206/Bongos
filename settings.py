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


import os
_basedir = os.path.abspath(os.path.dirname(__file__))

# application config
DEBUG = True

# web config
PORT = 80
HOST = '0.0.0.0'
SECRET_KEY = '4bt!\t\x97\xde\xa5R\xfbu\xc0\xe5\x8f\xe0Fz\x00\xa2P\x8d\x85\x97\x08'

# fabric config
POOL_SIZE = 250           # default is 250
PING_COUNT = 5            # default is 6
PING_TIMEOUT = 5          # default is 5
SSH_TIMEOUT = 30          # default is 30
SSH_COMMAND_TIMEOUT = 60  # default is 60

# database config
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'sqlite.db')
OPERATE_LISTS = 'operate_lists'
SSH_DETECT_LIST = 'ssh_detect_list'
PING_DETECT_LIST = 'ping_detect_list'
CUSTOM_OPERATE_LIST = 'custom_operate_list'
PREDEFINED_OPERATE_LIST = 'predefined_operate_list'