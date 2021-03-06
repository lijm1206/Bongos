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

# web config
PORT = 80
HOST = '0.0.0.0'
DOMAIN_NAME = 'BongosProject'
SESSION_PROTECTION = 'strong'
PRIVATE_KEY_PATH = os.path.join(_basedir, 'data/private_key')
SECRET_KEY = os.urandom(24)
DEBUG = False 

# api config
API_ACCESS_CLIENTS = ['127.0.0.1']
API_BASIC_URL = 'http://127.0.0.1/api'
WEIXIN_TOKEN = 'BongosProject'

# fabric config
POOL_SIZE = 250             # default is 250
PING_COUNT = 4              # default is 4
PING_TIMEOUT = 5            # default is 5
SSH_TIMEOUT = 30            # default is 30
SSH_COMMAND_TIMEOUT = 120   # default is 60
DISABLE_KNOWN_HOSTS = True  # default is True
FABRIC_FILE_PATH = os.path.join(_basedir, 'backend/fabfiles')

# database config
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'sqlite.db')
BASIC_PERMISSION_LIST = os.path.join(_basedir, 'data/ACL.txt')

# logging config
LOGGING_LEVEL = 'WARNING'
LOGGING_FILENAME = os.path.join(_basedir, 'bongos.log')
