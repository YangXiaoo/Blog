# coding: utf-8
from __future__ import division 
import uuid 
import urllib
from collections import Iterable

from django.db.models import Count
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseNotFound
from django.http import HttpResponse
from django.db.models import Q

from myweb.api import *
from myweb.models import *
# from myweb.forms import *
from myweb.settings import MAIL_ENABLE
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


@defendAttack
def login(request):
    '''
    登录
    '''
    error = ''
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('index'))
    if request.method == 'GET':
        return render_to_response('login.html')
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            userinfo = get_object(Users, username=username)
            if userinfo is not None:
                if userinfo.is_active == 1:
                    request.session['role_id'] = 0
                    request.session.set_expiry(3600)
                    return HttpResponseRedirect(reverse('blog/index'))
                else:
                    error = '用户未激活'
            else:
                error = '用户或密码错误'
        else:
            error = '用户名或密码未正确输入'
    return render_to_response('blog/login.html',{'error':error})


@login_required(login_url='/login')
def logout(request):
    '''
    注销
    '''
    request.session['role_id'] = ''
    logout(request)

    return HttpResponseRedirect(reverse('blog/index'))


def index(request):
    '''
    主页
    '''
    papers = Paper.objects.all()
    return render_to_response('blog/index.html', locals(), context_instance=RequestContext(request))


def category_detail(request):
    pass


def paper_detail(request):
    pass


def blog_paper_list(object):
    pass