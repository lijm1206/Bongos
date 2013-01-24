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


from flask.ext.wtf import Form, TextAreaField, HiddenField, SubmitField, QuerySelectField

from web.models.dashboard import SshConfig, PreDefinedScript


class CreateSshDetectForm(Form):

    next = HiddenField()
    server_list = TextAreaField(u'服务器列表:', id='textarea', description=u'支持域名或IP地址,一行一个.', default=u'None')
    ssh_config = QuerySelectField(u'SSH配置:', id='select', description=u'SSH配置.包含SSH端口,用户名,密码以及密钥(可选).', query_factory=SshConfig.query.all,  get_label='desc')
    submit = SubmitField(u'Continue', id='submit')

class CreatePingDetectForm(Form):

    next = HiddenField()
    server_list = TextAreaField(u'服务器列表:', id='textarea', description=u'支持域名或IP地址,一行一个.', default=u'None')
    submit = SubmitField(u'Continue', id='submit')

class CreatePreDefinedOperateForm(Form):

    vars_desc = u'''<p>用<code>|</code> 作为key(域名或IP地址)和value的分隔符</p>
<p>用<code>,</code> 作为多个变量赋值的分隔符</p>
<p>用<code>=</code> 作为变量赋值的分隔符</p>
<strong>例如:</strong>
<p><code>60.175.193.194|address=61.132.226.195,gateway=61.132.226.254</code></p>'''

    next = HiddenField()
    server_list = TextAreaField(u'服务器列表:', id='textarea', description=u'支持域名或IP地址,一行一个.', default=u'None')
    script_list = QuerySelectField(u'预定义脚本:', id='select', description=u'较为常用的预定义脚本.', query_factory=PreDefinedScript.query.all,  get_label='name')
    template_vars = TextAreaField(u'模板变量:', id='textarea', description=vars_desc, default=u'None')
    ssh_config = QuerySelectField(u'SSH配置', id='select', description=u'SSH配置.包含SSH端口,用户名,密码以及密钥(可选).', query_factory=SshConfig.query.all,  get_label='name')
    submit = SubmitField(u'Continue', id='submit')

class CreateCustomOperateForm(Form):

    script_desc = u'''<p>用<code>{</code>和<code>}</code>作为外部变量的定界符,模板中此类变量会自动按照变量文件中的定义进行替换.</p>
<p>同时模板依然支持shell中的<code>$</code>变量</p>
<pre>for device in `/sbin/ifconfig -a | awk '/^e/ { print $1 }'`; do
    mac=`ifconfig $device | grep HWaddr | awk '{ print $5 }'`
    if [ "$device" == "eth0" -o "$device" == "em1" ]; then
        echo "DEVICE=$device"    > /etc/sysconfig/network-scripts/ifcfg-$device
        echo "TYPE=Ethernet"     >> /etc/sysconfig/network-scripts/ifcfg-$device
        echo "BOOTPROTO=static"  >> /etc/sysconfig/network-scripts/ifcfg-$device
        echo "HWADDR=$mac"       >> /etc/sysconfig/network-scripts/ifcfg-$device
        echo "IPADDR={address}"  >> /etc/sysconfig/network-scripts/ifcfg-$device
        echo "NETMASK={netmask}" >> /etc/sysconfig/network-scripts/ifcfg-$device
        echo "GATEWAY={gateway}" >> /etc/sysconfig/network-scripts/ifcfg-$device
        echo "ONBOOT=yes"        >> /etc/sysconfig/network-scripts/ifcfg-$device
    fi
done</pre>'''

    vars_desc = u'''<p>用<code>|</code> 作为key(域名或IP地址)和value的分隔符</p>
<p>用<code>,</code> 作为多个变量赋值的分隔符</p>
<p>用<code>=</code> 作为变量赋值的分隔符</p>
<strong>例如:</strong>
<p><code>60.175.193.194|address=61.132.226.195,gateway=61.132.226.254</code></p>'''

    next = HiddenField()
    server_list = TextAreaField(u'服务器列表:', id='textarea', description=u'支持域名或IP地址,一行一个.', default=u'None')
    template_script = TextAreaField(u'脚本/脚本模板:', id='textarea', description=script_desc, default=u'None')
    template_vars = TextAreaField(u'模板变量:', id='textarea', description=vars_desc, default=u'None')
    ssh_config = QuerySelectField(u'SSH配置', id='select', description=u'SSH配置.包含SSH端口,用户名,密码以及密钥(可选).', query_factory=SshConfig.query.all,  get_label='name')
    submit = SubmitField(u'Continue', id='submit', description='submit')