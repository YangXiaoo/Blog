# coding: utf-8
from __future__ import division 
import uuid 
import urllib
import time
import json
from collections import Iterable

from django.db.models import Count
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseNotFound
from django.http import HttpResponse
from django.db.models import Q


from myweb.api import *
from myweb.models import *
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
                    return HttpResponseRedirect(reverse('login'))
                else:
                    error = '用户未激活'
            else:
                error = '用户或密码错误'
        else:
            error = '用户名或密码未正确输入'
    return render_to_response('login.html',{'error':error})


@login_required(login_url='/login')
def logout(request):
    '''
    注销
    '''
    request.session['role_id'] = ''
    logout(request)

    return HttpResponseRedirect(reverse('login'))


def index(request):
    '''
    主页
    '''
    return render_to_response('admin/index.html', locals(), context_instance=RequestContext(request))


def category_list(request):
    """
    文章分类
    """
    cate = Category.objects.all()
    return render_to_response('admin/category/category_list.html', locals(), context_instance=RequestContext(request))


def category_add(request):
    if request.method == "POST":
        cate_name = request.POST.get('category_name','')
        cate_description = request.POST.get('decription','')
        cate_status = request.POST.get('status','')
        cate_sort = request.POST.get('sorts','')
        cate_secrete = request.POST.get('secrete','')
        cate = Category(category_name=cate_name, description=cate_description, status=cate_status, sorts=cate_sort, secrete=cate_secrete)
        cate.save()
        return render_to_response('admin/category/category_list.html')
    return render_to_response('admin/category/category_add.html', locals(), context_instance=RequestContext(request))


def category_edit(request):
    if request.method == "POST":
        pass
    elif request.method == "GET":
        cid = request.GET.get('cid', '')
        if cid:
            c = getObject(Category, id=cid)
            return render_to_response('admin/category/category_edit.html', locals(), context_instance=RequestContext(request))
        cid = request.GET.get('id', '')
        c_name = request.GET.get('name', '')
        category = getObject(Category, id=cid)
        if c_name not in ['False', 'True']:
            category.category_name = c_name
        else:
            category.status = c_name
        try:
            category.save()
            status = 1
            info = 'ok'
        except:
            status = 0
            info = 'fail'
        return HttpResponse(json.dumps({
                    "status": status,
                    "info": info
                })) 


def paper_list(request):
    papers = Paper.objects.all()
    return render_to_response('admin/paper/paper_list.html', locals(), context_instance=RequestContext(request))


def paper_add(request):
    if request.method == "POST":
        cid = request.POST.get('typeid','')
        title = request.POST.get('title','')
        tag = request.POST.get('tag','')
        jumplink = request.POST.get('jumplink','')
        litpic = request.POST.get('litpic','')
        content = request.POST.get('content','')
        author = request.POST.get('author','')
        source = request.POST.get('source','')
        keywords = request.POST.get('keywords','')
        description = request.POST.get('description','')
        views = request.POST.get('views','')
        like = request.POST.get('like','')
        dislike = request.POST.get('dislike','')
        status = request.POST.get('status','')
        data = request.POST.get('create_time','')
        paper = Paper(cid=cid, title=title, tag=tag, jumplink=jumplink,litpic=litpic, content=content, author=author, source=source, keywords=keywords, description=description, views=views, like=like, dislike=dislike, status=status, data=data)
        paper.save()
        return render_to_response('admin/paper/paper_list.html')
    cate = Category.objects.all()
    return render_to_response('admin/paper/paper_add.html', locals(), context_instance=RequestContext(request))


def paper_edit(request):
    if request.method == "POST":
        id = request.POST.get('pid','')
        cid = request.POST.get('typeid','')
        title = request.POST.get('title','')
        tag = request.POST.get('tag','')
        jumplink = request.POST.get('jumplink','')
        litpic = request.POST.get('litpic','')
        content = request.POST.get('content','')
        author = request.POST.get('author','')
        source = request.POST.get('source','')
        keywords = request.POST.get('keywords','')
        description = request.POST.get('description','')
        views = request.POST.get('views','')
        like = request.POST.get('like','')
        dislike = request.POST.get('dislike','')
        status = request.POST.get('status','')
        data = request.POST.get('create_time','')
        paper = getObject(Paper, id=id)
        paper.update(id=id, cid=cid, title=title, tag=tag, jumplink=jumplink,litpic=litpic, content=content, author=author, source=source, keywords=keywords, description=description, views=views, like=like, dislike=dislike, status=status, data=data)
        return render_to_response('admin/paper/paper_list.html')
    elif request.method == "GET":
        pid = request.GET.get('pid', '')
        p = getObject(Paper, id=pid)
    return render_to_response('admin/paper/paper_edit.html', locals(), context_instance=RequestContext(request))


def paper_del(request):
    if request.method == "GET":
        pid = request.GET.get('pid', '')
        p = getObject(Paper, id=pid)
        try:
            p.delete()
            status = 1
            info = 'ok'
        except:
            status = 0
            info = 'fail'
        return HttpResponse(json.dumps({
                    "status": status,
                    "info": info
                })) 