#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 Ruoyan Wong(@saipanno).
#
#                    Created at 2013/07/29.
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


import json
import requests
from fabric.api import env, hide, execute

from backend.logger import logger
from backend.libs.utility import generate_private_path
from backend.libs.basic_remote_runner import basic_remote_runner


def fabfile_execute(operation, config, tasks):
    """
    :Return:

        0: 执行中
        1: 已完成
        2: 内部错误

    """

    ID = operation.get('OPT_ID', 0)
    API_URL = '%s/operation/%s' % (config.get('SETTINGS_API_BASIC_URL', None), ID)

    env.user = operation.get('SSH_USERNAME', 'root')
    env.password = operation.get('SSH_PASSWORD', 'password')
    env.port = operation.get('SSH_PORT', 22)
    env.key_filename = generate_private_path(operation.get('SSH_PRIVATE_KEY', 'default.key'),
                                             config.get('SETTINGS_PRIVATE_KEY_PATH'))

    task = tasks.get(operation.get('FABFILE_NAME', 'default'), None)

    with hide('everything'):
        connectivity = execute(basic_remote_runner, 'ls', dict(), stderr=True,
                               hosts=operation.get('OPT_SERVER_LIST', '').split())

    connectivity_nodes = list()
    for (k, v) in connectivity.items():
        if v.get('code', 1) == 0:
            connectivity_nodes.append(k)

    with hide('everything'):

        result = execute(task, ext_vars=json.loads(operation.get('OPT_EXT_VARIABLES', dict())),
                         hosts=connectivity_nodes)

    connectivity.update(result)

    data = json.dumps(dict(id=ID, status=1, result=connectivity),  ensure_ascii=False)

    response = requests.put(API_URL, data=data, headers={'content-type': 'application/json'})

    if response.status_code != requests.codes.ok:
        message = response.json.get('message', 'unknown errors')
        logger.error(u'UPDATE OPERATION FAILS| Operation ID is %s, Message is %s' % (ID, message))