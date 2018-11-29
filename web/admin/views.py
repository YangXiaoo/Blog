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

from markdown import markdown
import html2text as ht

@defendAttack
def login(request):
    '''
    登录
    '''
    error = ''
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('admin_index'))
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


def admin_index(request):
    '''
    主页
    '''
    return render_to_response('admin/admin_index.html', locals(), context_instance=RequestContext(request))


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
        return HttpResponseRedirect(reverse('category_list'))
    return render_to_response('admin/category/category_add.html', locals(), context_instance=RequestContext(request))


def category_edit(request):
    if request.method == "POST":
        cid = request.POST.get('cid', '')
        cate_name = request.POST.get('category_name','')
        cate_description = request.POST.get('decription','')
        cate_status = request.POST.get('status','')
        cate_sort = request.POST.get('sorts','')
        cate_secrete = request.POST.get('secrete','')
        Category.objects.filter(id=cid).update(category_name=cate_name, description=cate_description, status=cate_status, sorts=cate_sort, secrete=cate_secrete)
        return HttpResponseRedirect(reverse('category_list'))
    elif request.method == "GET":
        cid = request.GET.get('cid', '')
        c = getObject(Category, id=cid)
        return render_to_response('admin/category/category_edit.html', locals(), context_instance=RequestContext(request))


def category_edit_inline(request):
    if request.method == "GET":
        cid = request.GET.get('id', '')
        c_name = request.GET.get('name', '')
        status = request.GET.get('status','')
        secrete = request.GET.get('secrete','')
    elif request.method == "POST":
        cid = request.POST.get('id', '')
        c_name = request.POST.get('name', '')
        status = request.POST.get('status','')
        secrete = request.POST.get('secrete','')
    category = getObject(Category, id=cid)
    papers = Paper.objects.filter(cid=cid)
    try:
        if status != '':
            category.status = status
            for p in papers:
                p.status = status
                p.save()
        elif secrete != '':
            category.secrete = secrete
        else:
            category.category_name = c_name
            for p in papers:
                p.category = c_name
                p.save()
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


def category_del(request):
    if request.method == "GET":
        cid = request.GET.get('cid', '')
        c = getObject(Category, id=cid)
        try:
            papers = Paper.objects.filter(cid=cid)
            for p in papers:
                p.delete()
            c.delete()
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
        views = request.POST.get('views', 0)
        like = request.POST.get('like', 0)
        dislike = request.POST.get('dislike', 0)
        status = request.POST.get('status', 1)
        data = request.POST.get('create_time',time.strftime('%Y-%m-%d',time.localtime(time.time())))
        category = getObject(Category, id=cid).category_name
        paper = Paper(cid=cid, title=title, category=category, tag=tag, jumplink=jumplink,litpic=litpic, content=content, author=author, source=source, keywords=keywords, description=description, views=views, like=like, dislike=dislike, status=status, data=data)
        paper.save()
        category = getObject(Category, id=cid)
        category.paper_total += 1
        category.save()
        return HttpResponseRedirect(reverse('paper_list'))
    cate = Category.objects.all()
    return render_to_response('admin/paper/paper_add.html', locals(), context_instance=RequestContext(request))


def paper_edit(request):
    if request.method == "POST":
        id = request.POST.get('pid','')
        cid = request.POST.get('typeid','')
        category = getObject(Category, id=cid).category_name
        title = request.POST.get('title','')
        tag = request.POST.get('tag','')
        jumplink = request.POST.get('jumplink','')
        litpic = request.POST.get('litpic','')
        content = request.POST.get('content','')
        author = request.POST.get('author','')
        source = request.POST.get('source','')
        keywords = request.POST.get('keywords','')
        description = request.POST.get('description','')
        views = request.POST.get('views', 0)
        like = request.POST.get('like', 0)
        dislike = request.POST.get('dislike', 0)
        status = request.POST.get('status','')
        data = request.POST.get('create_time',time.strftime('%Y-%m-%d',time.localtime(time.time())))
        paper = getObject(Paper, id=id)
        Paper.objects.filter(id=id).update(cid=cid, category=category, title=title, tag=tag, jumplink=jumplink,litpic=litpic, content=content, author=author, source=source, keywords=keywords, description=description, views=views, like=like, dislike=dislike, status=status, data=data)
        return HttpResponseRedirect(reverse('paper_list'))
    elif request.method == "GET":
        pid = request.GET.get('pid', '')
        p = getObject(Paper, id=pid)
        text_maker = ht.HTML2Text()
        p.content = text_maker.handle(p.content)
        cate = Category.objects.all()
        return render_to_response('admin/paper/paper_edit.html', locals(), context_instance=RequestContext(request))


def paper_edit_inline(request):
    if request.method == "GET":
        pid = request.GET.get('id', )
        name = request.GET.get('name', '')
        status = request.GET.get('status','')
    elif request.method == "POST":
        pid = request.POST.get('id', )
        name = request.POST.get('name', '')
        status = request.POST.get('status','')
    paper = getObject(Paper, id=pid)

    try:
        if status != '':
            paper.status = status
        else:
            paper.title = name
        paper.save()
        status = 1
        info = 'ok'
    except:
        status = 0
        info = 'fail'
    return HttpResponse(json.dumps({
                "status": status,
                "info": info
            })) 


def paper_del(request):
    if request.method == "GET":
        pid = request.GET.get('pid', '')
        p = getObject(Paper, id=pid)
        try:
            category = getObject(Category, id=p.cid)
            category.paper_total -= 1
            category.save()
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


def test(request):
    if request.method == "POST":
        pass
    return render_to_response('admin/test.html', locals(), context_instance=RequestContext(request))