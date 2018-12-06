#!/usr/bin/python
# coding: utf-8
# 2018-11-26

import os, sys, time, json
import subprocess
import uuid
import urllib2
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


def page_list_return(total, current=1):
    """
    分页，返回本次分页的最小页数到最大页数列表
    """
    min_page = current - 2 if current - 4 > 0 else 1
    max_page = min_page + 4 if min_page + 4 < total else total

    return range(min_page, max_page + 1)

    '''
    from django.core.paginator import Paginator
    objects = ['john','paul','george','ringo','lucy','meiry','checy','wind','flow','rain']<br>
    p = Paginator(objects,3)  # 3条数据为一页，实例化分页对象
    print p.count  # 10 对象总共10个元素
    print p.num_pages  # 4 对象可分4页
    print p.page_range  # xrange(1, 5) 对象页的可迭代范围
     
    page1 = p.page(1)  # 取对象的第一分页对象
    print page1.object_list  # 第一分页对象的元素列表['john', 'paul', 'george']
    print page1.number  # 第一分页对象的当前页值 1
     
    page2 = p.page(2)  # 取对象的第二分页对象
    print page2.object_list  # 第二分页对象的元素列表 ['ringo', 'lucy', 'meiry']
    print page2.number  # 第二分页对象的当前页码值 2
     
    print page1.has_previous()  # 第一分页对象是否有前一页 False
    print page1.has_other_pages()  # 第一分页对象是否有其它页 True
     
    print page2.has_previous()  # 第二分页对象是否有前一页 True
    print page2.has_next()  # 第二分页对象是否有下一页 True
    print page2.next_page_number()  # 第二分页对象下一页码的值 3
    print page2.previous_page_number()  # 第二分页对象的上一页码值 1
    print page2.start_index()  # 第二分页对象的元素开始索引 4
    print page2.end_index()  # 第2分页对象的元素结束索引 6
    '''

def pages(post_objects, request):
    """
    page public function , return page's object tuple
    分页公用函数，返回分页的对象元组
    """
    paginator = Paginator(post_objects, 20) # 每页20条数据
    try:
        current_page = int(request.GET.get('page', '1')) 
    except ValueError:
        current_page = 1

    page_range = page_list_return(len(paginator.page_range), current_page)

    try:
        page_objects = paginator.page(current_page)
    except (EmptyPage, InvalidPage):
        page_objects = paginator.page(paginator.num_pages)

    if current_page >= 5:
        show_first = 1
    else:
        show_first = 0

    if current_page <= (len(paginator.page_range) - 3):
        show_end = 1
    else:
        show_end = 0

    # 所有对象， 分页器， 本页对象， 所有页码， 本页页码，是否显示第一页，是否显示最后一页
    return post_objects, paginator, page_objects, page_range, current_page, show_first, show_end


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


def get_area(ip):
    ak =  'hGK861NGVlSbxiVnBHqF0lICUeiUBVhp' 
    url = 'https://api.map.baidu.com/location/ip?ip=%s&ak=%s&coor=bd09ll' % (str(ip), ak)
    urlobject = urllib2.urlopen(url)  
    urlcontent = urlobject.read()  
    res = json.loads(urlcontent)
    return res

