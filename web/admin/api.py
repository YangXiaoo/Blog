#!/usr/bin/python
# coding: utf-8
# 2018-11-26

import os, sys, time, pwd
import subprocess
import uuid
import django
from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse

from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.core.mail import send_mail
from email.mime.text import MIMEText
from email.utils import formataddr
from smtplib import SMTP, SMTP_SSL, SMTPAuthenticationError, SMTPConnectError, SMTPSenderRefused
 
from admin.models import *
from myweb.settings import *

os.environ['DJANGO_SETTINGS_MODULE'] = 'myweb.settings'

def bash(cmd):
    '''
    执行bash命令
    '''
    return subprocess.call(cmd, shell=True)

def getMacAddress():
    '''
    获得服务端的mac地址
    '''
    node = uuid.getnode()
    mac = uuid.UUID(int=node).hex[-12:]
    return mac

def getObject(model, **kwargs):
    '''
    数据库查询
    '''
    for value in kwargs.values():
        if not value:
            return None
    the_object = model.objects.filter(**kwargs)
    if len(the_object) == 1:
        the_object = the_object[0]
    else:
        the_object = None
    return the_object

def colorPrint(msg, color='red', exits=False):
    """
    颜色打印字符或者退出
    参考：https://www.cnblogs.com/hellojesson/p/5961570.html
    """
    color_msg = {'blue': '\033[1;36m%s\033[0m',
                 'green': '\033[1;32m%s\033[0m',
                 'yellow': '\033[1;33m%s\033[0m',
                 'red': '\033[1;31m%s\033[0m',
                 'title': '\033[30;42m%s\033[0m',
                 'info': '\033[32m%s\033[0m'}
    msg = color_msg.get(color, 'red') % msg  
    print(msg)
    if exits:
        time.sleep(2)
        sys.exit()
    return msg


def defendAttack(func):
    def _deco(request, *args, **kwargs):
        if int(request.session.get('visit', 1)) > 10:
            logger.debug('请求次数: %s' % request.session.get('visit', 1))
            Frobidden = '<h1>Forbidden.403.请求次数过多，请稍后再试。</h1>'
            return HttpResponse(Frobidden, status=403)
        request.session['visit'] = request.session.get('visit', 1) + 1
        request.session.set_expiry(300)
        return func(request, *args, **kwargs)
    return _deco

def mkdir(dir_name, username='', mode=755):
    """
    目录存在，如果不存在就建立，并且权限正确
    """
    cmd = '[ ! -d %s ] && mkdir -p %s && chmod %s %s' % (dir_name, dir_name, mode, dir_name)
    bash(cmd)
    if username:
        chown(dir_name, username)

def chown(path, user, group=''):
    if not group:
        group = user
    try:
        uid = pwd.getpwnam(user).pw_uid
        gid = pwd.getpwnam(group).pw_gid
        os.chown(path, uid, gid)
    except KeyError:
        pass

def get_tmp_dir(dirs='static/files'):
    seed = uuid.uuid4().hex[:4]
    now = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    file_path = '%s-%s' % (now, seed)
    path = os.path.join(BASE_DIR, dirs)
    dir_name = os.path.join(path, file_path)
    mkdir(dir_name, mode=777)
    return dir_name,file_path

def get_client_ip(request):
    try:
        real_ip = request.META['HTTP_X_FORWARDED_FOR']
        ip = real_ip.split(",")[0]
    except:
        try:
            ip = request.META['REMOTE_ADDR']
        except:
            ip = ""
    return ip


def require_login(func):
    """
    用户验证
    """
    def _deco(request, *args, **kwargs):
        if request.session.get('role_id', '') != 0:
            return HttpResponseRedirect(reverse('login'))
        else:
            return func(request, *args, **kwargs)
    return _deco


def admin_require_login(func):
    """
    用户验证
    """
    def _deco(request, *args, **kwargs):
        if request.session.get('role_id', '') != 0:
            return render_to_response(reverse('admin_login'))
        else:
            return func(request, *args, **kwargs)
    return _deco