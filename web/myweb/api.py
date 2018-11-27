#!/usr/bin/python
# coding: utf-8
# 2018-11-26

import os, sys, time
import subprocess
import uuid
import django
from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from settings import *
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.core.mail import send_mail
from email.mime.text import MIMEText
from email.utils import formataddr
from smtplib import SMTP, SMTP_SSL, SMTPAuthenticationError, SMTPConnectError, SMTPSenderRefused

from myweb.models import Users
from myweb.settings import MAIL_ENABLE

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