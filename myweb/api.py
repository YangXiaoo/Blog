#!/usr/bin/python
# coding: utf-8
# 2018-11-26

import os, sys, time, json
import subprocess
import uuid
import urllib, urllib2, urlparse
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

from myweb.models import Comment
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


def defendAttack(func):
    def _deco(request, *args, **kwargs):
        if int(request.session.get('visit', 1)) > 10:
            logger.debug('请求次数: %s' % request.session.get('visit', 1))
            error = 'Forbidden(403),请求次数过多,请稍后再试。'
            return render_to_response('blog/error/404.html',{'error':error})
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


def reply(pid):
    reply_comment = Comment.objects.filter(pcid=pid)
    if not reply_comment:
        reply_comment = [0]
    return reply_comment

def is_reply(pid):
    reply_comment = Comment.objects.filter(pcid=pid)
    if not reply_comment:
        return 0
    return 1

def reply_user(cid,ruid):
    comment = getObject(Comment, id=cid)
    if comment.ruid == ruid:
        return 0
    return 1


class OAuthQQ:
    def __init__(self):
        self.client_id = CLIENT_ID
        self.client_key = CLIENT_KEY
        self.redirect_uri = REDIRECT_URL

    def get_auth_url(self):
        """获取授权页面的网址"""
        params = {'client_id': self.client_id,
                  'response_type': 'code',
                  'redirect_uri': self.redirect_uri,
                  'scope': 'get_user_info',
                  'state': 1}
        url = 'https://graph.qq.com/oauth2.0/authorize?%s' % urllib.urlencode(params)
        return url

    def get_access_token(self, code):
            """根据code获取access_token"""
            params = {'grant_type': 'authorization_code',
                      'client_id': self.client_id,
                      'client_secret': self.client_key,
                      'code': code,
                      'redirect_uri': self.redirect_uri}    # 回调地址
            url = 'https://graph.qq.com/oauth2.0/token?%s' % urllib.urlencode(params)

            # 访问该网址，获取access_token
            response = urllib2.urlopen(url).read()
            result = urlparse.parse_qs(response, True)

            access_token = str(result['access_token'][0])
            self.access_token = access_token
            return access_token


    def get_open_id(self):
            """获取QQ的OpenID"""
            params = {'access_token': self.access_token}
            url = 'https://graph.qq.com/oauth2.0/me?%s' % urllib.urlencode(params)

            response = urllib2.urlopen(url).read()
            v_str = str(response)[9:-3]  # 去掉callback的字符
            v_json = json.loads(v_str)

            openid = v_json['openid']
            self.openid = openid
            return openid

    def get_qq_info(self):
        """获取QQ用户的资料信息"""
        params = {'access_token': self.access_token,
                  'oauth_consumer_key': self.client_id,
                  'openid': self.openid}
        url = 'https://graph.qq.com/user/get_user_info?%s' % urllib.urlencode(params)

        response = urllib2.urlopen(url).read()
        return json.loads(response)