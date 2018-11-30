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

from markdown import markdown

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
            userinfo = getObject(Users, username=username)
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

    return HttpResponseRedirect(reverse('blog/blog_index'))


def blog_index(request):
    '''
    主页
    '''
    category = Category.objects.filter(status=1)
    cid = []
    for c in category:
        cid.append(c.id)
    papers = Paper.objects.filter(Q(cid__in=cid)&Q(status=1))
    return render_to_response('blog/blog_index.html', locals(), context_instance=RequestContext(request))


def category_detail(request):
    if request.method == "GET":
        cid = request.GET.get('cid', '')
        category_name = getObject(Category, id=cid).category_name
        papers = Paper.objects.filter(cid=cid)
    return render_to_response('blog/category_detail.html', locals(), context_instance=RequestContext(request))


def paper_detail(request):
    if request.method == "GET":
        pid = request.GET.get('pid', '')
        p = getObject(Paper, id=pid)
    return render_to_response('blog/paper_detail.html', locals(), context_instance=RequestContext(request))


def blog_category_list(request):
    cate = Category.objects.filter(status=1)
    paper_total = len(cate)
    return render_to_response('blog/blog_category_list.html', locals(), context_instance=RequestContext(request))


def blog_search(request):
    pass