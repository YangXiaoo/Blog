# coding:UTF-8
import uuid 
import urllib
import time
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.db.models import Q

from myweb.api import *
from myweb.models import *
from myweb.settings import *


from admin.models import *
from admin.api import require_login,send_mail

from email.mime.text import MIMEText
from email.header import Header

WEB_URL = 'http://www.lxa.kim'
WEB_TITLE = '杨潇-博客'

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
                user.last_ip = ip 
                user.log_total += 1
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
        user = Users(username=username, password=password, profile=default_img, last_ip=ip, log_total=1)

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
    if request.session.get('role_id', '') == 0:
        category = Category.objects.filter(status=1)
    else:
        category = Category.objects.filter(Q(status=1)&Q(secrete=0))
    cid = []
    for c in category:
        cid.append(c.id)
    papers = Paper.objects.filter(Q(cid__in=cid)&Q(status=1))
    return render_to_response('blog/blog_index.html', locals(), context_instance=RequestContext(request))


def category_detail(request):
    if request.method == "GET":
        cid = request.GET.get('cid', '')
        cate = getObject(Category, id=cid)
        if cate.status == 0:
            error = '404, 该资源无法查看'
            return render_to_response('blog/404.html',{'error':error})
        if cate.secrete == 1:
            if request.session.get('role_id', '') != 0:
                error = '该内容需要登录才能查看'
                return render_to_response('blog/login.html',{'error':error}) 
        category_name = cate.category_name
        if request.session.get('role_id', '') != 0:
            papers = Paper.objects.filter(Q(cid=cid)&Q(status=1)&Q(secrete=0))
        else:
            papers = Paper.objects.filter(Q(cid=cid)&Q(status=1))
    return render_to_response('blog/category_detail.html', locals(), context_instance=RequestContext(request))


def paper_detail(request):
    if request.method == "GET":
        pid = request.GET.get('pid', '')
        p = getObject(Paper, id=pid)
        if p.status == 0:
            error = '404, 该资源无法查看'
            return render_to_response('blog/404.html',{'error':error})
        if p.secrete == 1:
            error = '该内容需要登录才能查看'
            return render_to_response('blog/login.html',{'error':error})
        p.views += 1
        p.save()
        ip = get_client_ip(request)
        try:
            uid = request.COOKIES.get('uid',-1)
            # ret = get_area(ip)
            # if ret.get('status') == 'success':
            view_log = Viewlog(uid=uid, ip=ip, pid=pid)
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
        uid = request.COOKIES.get('uid', -1)
        ip = get_client_ip(request)
        if int(kind) == 0:
            thumb = Thumbs(uid=uid, ip=ip, pid=pid, is_dislike=1)
            paper.dislike += 1
            info = "emmmmmmmmmmm...."
        else:
            thumb = Thumbs(uid=uid, ip=ip, pid=pid)
            paper.like += 1
            info = "谢谢你的支持"
        try:
            thumb.save()
            paper.save()
            status = 1
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
        create_time = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        comment = Comment(pid=pid, uid=uid, ruid=ruid, pcid=pcid, content=content,data=create_time)
        comment.save()
        ruser = getObject(Users, id=ruid)
        user = getObject(Users, id=uid)
        mail = getObject(Emailsetting, status=1)
        paper = getObject(Paper, id=pid)
        config = Config.objects.all()
        if config:
            message_header = config[0].title
        else:
            message_header = WEB_TITLE
        mail_message = """
        <p> %s DD </p>
        <p> %s... </p>
        <a href="%s/blog/paper_detail/?pid=%s"> %s </a>
        """ % ('user.username', '', WEB_URL, 'pid', '')
        message = MIMEText(mail_message, 'html', 'utf-8')
        message['From'] = Header(message_header, 'utf-8')
        message['To'] = '评论回复'
        subject = '评论回复'
        message['Subject'] = Header(subject, 'utf-8')
        reciver = []
        if not ruser:
            reciver.append(mail.user)
        else:
            reciver.append(ruser.email)
        send_mail(mail, reciver, message.as_string())
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('blog_index')))