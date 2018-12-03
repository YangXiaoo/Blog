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


from admin.models import *
from admin.api import require_login

@defendAttack
def login(request):
    if request.method == "POST":
        username = request.POST.get('username', '')
        password = request.POST.get('password')
        user = getObject(Users, username=username)
        if user:
            if user.password == password:
                request.session['role_id'] = 0
                request.session['user_id'] = user.id
                request.session.set_expiry(3600)
                response= HttpResponseRedirect(reverse('blog_index'))
                response.set_cookie('profile',user.profile)
                response.set_cookie('username',user.username)
                response.set_cookie('uid', user.id)
                ip = get_client_ip(request)
                user.ip = ip 
                try:
                    ret = get_area(ip)
                    if ret.get('status') == 'success':
                        login_log = Loginlog(uid=user.id, name=user.username, ip=ip, province=ret.get('regionName'),city=ret.get('city'),isp=ret.get('isp'), lon=ret.get('lon'), lat=ret.get('lat'))
                        login_log.save()
                except:
                    pass
                user.save()
                return response
            else:
                error = '密码或账号错误'
        else:
            error = '账号不存在'
        return render_to_response('blog/login.html',{'error':error})
    return render_to_response('blog/login.html')



@require_login
def logout(request):
    '''
    注销
    '''
    del request.session['user_id']
    del request.session['role_id']
    response = HttpResponseRedirect(reverse('blog_index'))
    response.delete_cookie('uid')
    response.delete_cookie('username')
    response.delete_cookie('profile')
    return response



def sign(request):
    error = ''
    if request.method == "POST":
        password = request.POST.get('password', '')
        repassword = request.POST.get('repassword', '')
        if password != repassword:
            error = "两次密码输入不相同"
            return render_to_response('blog/sign.html',{'error':error})
        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        user = getObject(Users, username=username)
        if user:
            error = "用户存在"
            return render_to_response('blog/sign.html',{'error':error})

        config = Config.objects.all()
        if config:
            default_img = config[0].default_img
        else:
            default_img = ''
        ip = get_client_ip(request)
        user = Users(username=username, password=password, profile=default_img, last_ip=ip)

        try:
            user.save()
        except Exception as e:
            error = str(e)
            return render_to_response('blog/sign.html',{'error':error})

        try:
            user = getObject(Users,username=username)
            ret = get_area(ip)
            if ret[status] == 'success':
                login_log = Loginlog(uid=user.id, name=user.username, ip=ip,province=ret.get('regionName'),city=ret.get('city'),isp=ret.get('isp'), lon=ret.get('lon'), lat=ret.get('lat'))
                login_log.save()
        except:
            pass
        user = getObject(Users, username=username)
        request.session['role_id'] = 0
        request.session['user_id'] = user.id
        request.session.set_expiry(3600)
        response= render_to_response('blog/blog_index.html', {})
        response.set_cookie('profile',user.profile)
        response.set_cookie('username',user.username)
        response.set_cookie('uid', user.id)
        return response
    return render_to_response('blog/sign.html')



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
        p.views += 1
        p.save()
        ip = get_client_ip(request)
        try:
            uid = request.COOKIES.get('uid','')
            ret = get_area(ip)
            if ret.get('status') == 'success':
                view_log = Viewlog(uid=uid, ip=ip, pid=pid, isp=ret.get('isp'), lon=ret.get('lon'), lat=ret.get('lat'))
                view_log.save()
        except:
            pass
        comments = Comment.objects.filter(Q(pid=pid)&Q(pcid=-1)&Q(status=1))
        return render_to_response('blog/paper_detail.html', locals(), context_instance=RequestContext(request))


def blog_category_list(request):
    cate = Category.objects.filter(status=1)
    paper_total = len(cate)
    return render_to_response('blog/blog_category_list.html', locals(), context_instance=RequestContext(request))


def blog_search(request):
    pass


def blog_thumbs(request):
    if request.method == "GET":
        pid = request.GET.get('id', '')
        paper = getObject(Paper, id=pid)
        kind = request.GET.get('kind', '')
        uid = request.COOKIES.get('uid','')
        ip = get_client_ip()
        if kind == 0:
            thumb = Thumbs(uid=uid, ip=ip, pid=pid, is_dislike=1)
            paper.dislike += 1
        else:
            thumb = Thumbs(uid=uid, ip=ip, pid=pid)
            paper.like += 1
        try:
            thumb.save()
            paper.save()
            status = 1
            info = "谢谢你的支持"
        except Exception as e:
            status = 0
            info = "出问题了...<br>" + str(e)
        return HttpResponse(json.dumps({
                    "status": status,
                    "info": info
                })) 



def paper_comment(request):
    if request.method == "POST":
        ruid = request.POST.get('ruid', '')
        uid = request.POST.get('uid', '')
        pid = request.POST.get('pid', '')
        pcid = request.POST.get('pcid', '')
        content = request.POST.get('content', '')
        comment = Comment(pid=pid, uid=uid, ruid=ruid, pcid=pcid, content=content)
        comment.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('blog_index')))