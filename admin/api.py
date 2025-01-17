#!/usr/bin/python
# coding: utf-8
# 2018-11-26

import os, sys, time, pwd
import subprocess
import uuid
import django
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.core.paginator import Paginator, EmptyPage, InvalidPage

from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from smtplib import SMTP, SMTP_SSL, SMTPAuthenticationError, SMTPConnectError, SMTPSenderRefused
 
from admin.models import *
from myweb.api import get_area
from myweb.settings import *

os.environ['DJANGO_SETTINGS_MODULE'] = 'myweb.settings'
OLD_URL = ['www.lxa.kim', 'lxa.kim', 'www.lxxx.site', 'lxxx.site']

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
        if int(request.session.get('visit', 1)) > 50:
            Frobidden = '<h1>Forbidden.403.请求次数过多，请稍后再试。</h1>'
            return HttpResponse(Frobidden, status=403)
        if request.META['HTTP_HOST'] in OLD_URL:
            return render_to_response('old_url.html')
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
        if request.META['HTTP_HOST'] in OLD_URL:
            return render_to_response('old_url.html')
        if request.session.get('role_id', '') != 0:
            return HttpResponseRedirect(reverse('admin_login'))
        else:
            return func(request, *args, **kwargs)
    return _deco


def file_delete(file):
    bash('rm -f %s*' % file.dirs)



def test_mail(email):
    try:
        if email.port == 465:
            smtp = SMTP_SSL(email.host, port=email.port, timeout=10)
        else:
            smtp = SMTP(email.host, port=email.port, timeout=10)
        smtp.login(email.user, email.password)
        smtp.sendmail(email.user, (email.user, ),
                      '''From:%s\r\nTo:%s\r\nSubject:Mail Test!\r\n\r\n  Mail test passed!\r\n''' %
                      (email.user, email.user))
        smtp.quit()
        return True
    except Exception as e:
        return False


def send_mail(email, address, content):
    try:
        if email.port == 465:
            smtp = SMTP_SSL(email.host, port=email.port, timeout=10)
        else:
            smtp = SMTP(email.host, port=email.port, timeout=10)
        smtp.login(email.user, email.password)
        smtp.sendmail(email.user, address, content)
        smtp.quit()
        return True
    except Exception as e:
        return False



def get_client_type(agent):
    """
    判断用户端类型
    返回0：移动端
    返回1：PC端
    """
    pc_types = {
        'Opera' : 'Opera浏览器',
        'Firefox' : '火狐浏览器',
        'TaoBrowser':'淘宝浏览器',
        'LBBROWSER':'猎豹浏览器',
        'QQBrowser':'QQ浏览器', 
        'MetaSr':'搜狗浏览器',
        'Maxthon':'遨游浏览器', 
        'UBrowser':'UC浏览器',
        'Opera':'Opera',
        'Chrome':'谷歌浏览器',
        'Safari':'Safari'
        }
    mobile_type = {
        'iPad':'IPAD',
        'iPod' : 'iPod',
        'iPhone':'iPhone',
        'Android':'Android',
        'BlackBerry' : 'BlackBerry移动端',
        'hp-tablet':'WebOS HP Touchpad移动端',
        'MQQBrowser' : 'QQ浏览器移动端',
        'Presto' : 'Android Opera Mobile移动端',
        'Xoom' : 'Android Pad Moto Xoom移动端',
        'Windows Phone' : 'Windows Phone Mango移动端',
        'UCWEB' : 'UC移动端',
        'SogouMobileBrowser' : '搜狗移动端',
        '360SE' : '360移动端'
          }
    for k, v in mobile_type.items():
        if k in agent:
            return 0,v
    for k, v in pc_types.items():
        if k in agent:
            return 1,v
    return 'other', 'other'


def set_view(request):
    try:
        ip = get_client_ip(request)
        uid = request.COOKIES.get('uid',-1)
        ret = get_area(ip)
        agent = request.META.get('HTTP_USER_AGENT','')
        _,agent = get_client_type(agent)
        if ret.get('status', 1) == 0:
            view_log = Viewlog(uid=uid, ip=ip, pid='-1',lon=ret['content']['point']['x'], lat=ret['content']['point']['y'], agent=agent, province=ret['content']['address_detail']['province'],city=ret['content']['address_detail']['city'])
            view_log.save()
    except:
        pass