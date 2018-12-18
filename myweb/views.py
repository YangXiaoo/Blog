# coding:UTF-8
import uuid 
import urllib
import time
from django.shortcuts import render_to_response, render
from django.template import RequestContext, Template, Context
from django.http import HttpResponse
from django.db.models import Q


from myweb.api import *
from myweb.models import *
from myweb.settings import *


from admin.models import *
from admin.api import require_login,send_mail, get_client_type

from email.mime.text import MIMEText
from email.header import Header

WEB_URL = 'http://yangxiao.online'
WEB_TITLE = '杨潇-博客'

@defendAttack
def login(request):
    if request.method == "POST":
        username = request.POST.get('username', '')
        password = request.POST.get('password')
        user = getObject(Users, username=username)
        if user:
            if user.password == password:
                if user.is_admin == 1:
                    request.session['role_id'] = 0
                else:
                    request.session['role_id'] = 1
                request.session['user_id'] = user.id
                request.session.set_expiry(3600)
                response= HttpResponseRedirect(reverse('blog_index'))
                response.set_cookie('profile',user.profile)
                response.set_cookie('username',user.username)
                response.set_cookie('uid', user.id)
                ip = get_client_ip(request)
                user.last_ip = ip 
                user.log_total += 1
                # try:
                agent = request.META.get('HTTP_USER_AGENT','')
                _, agent = get_client_type(agent)
                ret = get_area(ip)
                if ret.get('status', 1) == 0:
                    login_log = Loginlog(uid=user.id, name=user.username, ip=ip, province=ret['content']['address_detail']['province'],city=ret['content']['address_detail']['city'],district=ret['content']['address_detail']['district'],lon=ret['content']['point']['x'], lat=ret['content']['point']['y'], agent=agent)
                    login_log.save()
                # except:
                #     pass
                user.save()
                return response
            else:
                error = '密码或账号错误'
        else:
            error = '账号不存在'
        return render_to_response('blog/login.html',{'error':error})
    return render_to_response('blog/login.html')


def qq_connect(request):
    """
    回调函数
    """
    request_code = request.GET.get('code')
    oauth_qq = OAuthQQ()

    # 获取access_token
    access_token = oauth_qq.get_access_token(request_code)
    time.sleep(0.05)  # 稍微休息一下，避免发送urlopen的10060错误
    open_id = oauth_qq.get_open_id()
    # 检查open_id是否存在
    user = getObject(Users, uuid=open_id)
    if user:
        # 存在则获取对应的用户，并登录
        if user.is_admin == 1:
            request.session['role_id'] = 0
        else:
            request.session['role_id'] = 1
        request.session['user_id'] = user.id
        request.session.set_expiry(3600)
        response= HttpResponseRedirect(reverse('blog_index'))
        response.set_cookie('profile',user.profile)
        response.set_cookie('username',user.username.encode('utf-8'))
        response.set_cookie('uid', user.id)
        ip = get_client_ip(request)
        user.last_ip = ip 
        user.log_total += 1
        try:
            agent = request.META.get('HTTP_USER_AGENT','')
            _, agent = get_client_type(agent)
            ret = get_area(ip)
            if ret.get('status', 1) == 0:
                login_log = Loginlog(uid=user.id, name=user.username, ip=ip, province=ret['content']['address_detail']['province'],city=ret['content']['address_detail']['city'],district=ret['content']['address_detail']['district'],lon=ret['content']['point']['x'], lat=ret['content']['point']['y'], agent=agent)
                login_log.save()
        except:
            pass
        user.save()
        return response
    else:
        # 不存在，则跳转到绑定用户页面
        infos = oauth_qq.get_qq_info()  # 获取用户信息
        url = '%s?open_id=%s&nickname=%s&profile=%s&gender=%s' % (reverse('bind_account_qq'), open_id, infos['nickname'], infos['figureurl_qq_1'], [1, 0][infos['gender'] == "男"])
        return HttpResponseRedirect(url)

def qq_login(request):
    oauth_qq = OAuthQQ()
    # 获取 得到Authorization Code的地址
    url = oauth_qq.get_auth_url()
    # 重定向到授权页面
    return HttpResponseRedirect(url)


def bind_account_qq(request):
    if request.method == "GET":
        open_id = request.GET.get('open_id', '')
        nickname = request.GET.get('nickname', '')
        profile = request.GET.get('profile', '')
        gender = request.GET.get('gender', '')
        return render_to_response('blog/bind/bind_account_qq.html', locals(), context_instance=RequestContext(request))
    elif request.method == "POST":
        open_id = request.POST.get('open_id', '')
        nickname =request.POST.get('nickname', '')
        profile = request.POST.get('profile', '')
        email = request.POST.get('email', '')
        gender = request.POST.get('gender', '')
        nickname += '*'
        user = getObject(Users, username=nickname)
        if user:
            error = "用户名重复"
            return render_to_response('blog/bind/bind_account_qq.html', locals(), context_instance=RequestContext(request))
        ip = get_client_ip(request)
        user = Users(username=nickname, password='-1', profile=profile, last_ip=ip, log_total=1, gender=gender, third_log=1, uuid=open_id, email=email)
        try:
            user.save()
        except Exception as e:
            error = str(e)
            return render_to_response('blog/bind/bind_account_qq.html', locals(), context_instance=RequestContext(request))
        try:
            agent = request.META.get('HTTP_USER_AGENT','')
            _,agent = get_client_type(agent)
            user = getObject(Users,username=nickname)
            ret = get_area(ip)
            if ret.get('status', 1) == 0:
                login_log = Loginlog(uid=user.id, name=user.username, ip=ip,province=ret['content']['address_detail']['province'],city=ret['content']['address_detail']['city'],district=ret['content']['address_detail']['district'],lon=ret['content']['point']['x'], lat=ret['content']['point']['y'],agent=agent)
                login_log.save()
        except:
            pass
        response= render_to_response('blog/blog_index.html', {})
        try:
            user = getObject(Users, username=nickname)
            request.session['role_id'] = 1
            request.session['user_id'] = user.id
            request.session.set_expiry(3600)
            response.set_cookie('profile',user.profile)
            response.set_cookie('username',user.username.encode('utf-8'))
            response.set_cookie('uid', user.id)
        except Exception as e:
            error = str(e)
            return render_to_response('blog/bind/bind_account_qq.html', locals(), context_instance=RequestContext(request))
        return response


@require_login
def logout(request):
    '''
    注销
    '''
    response = HttpResponseRedirect(reverse('blog_index'))
    try:
        del request.session['user_id']
        del request.session['role_id']
        response.delete_cookie('uid')
        response.delete_cookie('username')
        response.delete_cookie('profile')
    except:
        pass
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
            agent = request.META.get('HTTP_USER_AGENT','')
            _,agent = get_client_type(agent)
            user = getObject(Users,username=username)
            ret = get_area(ip)
            if ret.get('status', 1) == 0:
                login_log = Loginlog(uid=user.id, name=user.username, ip=ip,province=ret['content']['address_detail']['province'],city=ret['content']['address_detail']['city'],district=ret['content']['address_detail']['district'],lon=ret['content']['point']['x'], lat=ret['content']['point']['y'],agent=agent)
                login_log.save()
        except:
            pass
        user = getObject(Users, username=username)
        if user.is_admin == 1:
            request.session['role_id'] = 0
        else:
            request.session['role_id'] = 1
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
    if request.method == "POST":
        page = request.POST.get('page', '')
        start = (int(page) -  1) * 10
        if request.session.get('role_id', '') == 0:
            papers = Paper.objects.filter(status=1).order_by('-id')[start: start+10]
        else:
            papers = Paper.objects.filter(Q(status=1)&Q(secrete=0)).order_by('-id')[start: start+10]
        # return render_to_response('blog/paper_load_more.html', locals())
        ret = ''
        for p in papers:
            if p.is_jump == 0:
                ret += u"""<div class="list-arc-item "><a href="/blog/paper_detail/?pid=%s" title="%s"><div class="list-box"><h3>%s</h3><div class="info">%s</div></div></a><div class="tags font-ei "><i class="fa fa-lemon-o" title="tag：%s" data-toggle="tooltip"> %s</i>&nbsp;<i class="fa fa-clock-o" title="time：%s" data-toggle="tooltip" > %s</i>&nbsp;<i class="fa fa-commenting-o" title="comment：%s" data-toggle="tooltip" > %s</i>&nbsp;<i class="fa fa-thumbs-o-up" title="like：%s" data-toggle="tooltip" > %s</i>&nbsp;</div></div><hr>""" % (p.id, p.title, p.title, p.description, p.category, p.category, p.data, p.data, p.comment_total, p.comment_total, p.like, p.like)
            else:
                ret += u"""<div class="list-arc-item "><a href="%s" title="%s" target="_blank"><div class="list-box"><h3>%s</h3><div class="info">%s</div></div></a><div class="tags font-ei "><i class="fa fa-lemon-o" title="tag：%s" data-toggle="tooltip"> %s</i>&nbsp;<i class="fa fa-clock-o" title="time：%s" data-toggle="tooltip" > %s</i>&nbsp;<i class="fa fa-commenting-o" title="comment：%s" data-toggle="tooltip" > %s</i>&nbsp;<i class="fa fa-thumbs-o-up" title="like：%s" data-toggle="tooltip" > %s</i>&nbsp;</div></div><hr>""" % (p.jumplink, p.title, p.title, p.description, p.category, p.category, p.data, p.data, p.comment_total, p.comment_total, p.like, p.like)
        # ret = render_to_response('blog/paper_load_more.html', locals())
        # return HttpResponse((ret))
        status = [1, 0][len(papers) == 0]
        return HttpResponse(json.dumps({
                    "status": status,
                    "info": ret
                })) 

    if request.session.get('role_id', '') == 0:
        papers = Paper.objects.filter(status=1).order_by('-id')[:10]
    else:
        papers = Paper.objects.filter(Q(status=1)&Q(secrete=0))[:10]
    return render_to_response('blog/blog_index.html', locals(), context_instance=RequestContext(request))


def category_detail(request):
    if request.method == "GET":
        cid = request.GET.get('cid', '')
        cate = getObject(Category, id=cid)
        if cate:
            if cate.status == 0:
                error = '404, 该资源无法查看'
                return render_to_response('blog/error/404.html',{'error':error})
            if cate.secrete == 1:
                if request.session.get('role_id', '') != 0:
                    error = '该内容需要登录才能查看'
                    return render_to_response('blog/login.html',{'error':error}) 
            category_name = cate.category_name
            if request.session.get('role_id', '') != 0:
                papers = Paper.objects.filter(Q(cid=cid)&Q(status=1)&Q(secrete=0))
            else:
                papers = Paper.objects.filter(Q(cid=cid)&Q(status=1))
            return render_to_response('blog/category/category_detail.html', locals(), context_instance=RequestContext(request))
    elif request.method == "POST":
        cid = request.POST.get('id', '')
        page = request.POST.get('page', '')
        start = int(int(page) - 1) * 10
        cate = getObject(Category, id=cid)
        if cate:
            if cate.status == 0:
                error = '404, 该资源无法查看'
                return render_to_response('blog/eoor/404.html',{'error':error})
            if cate.secrete == 1:
                if request.session.get('role_id', '') != 0:
                    error = '该内容需要登录才能查看'
                    return render_to_response('blog/login.html',{'error':error}) 
            if request.session.get('role_id', '') != 0:
                papers = Paper.objects.filter(Q(cid=cid)&Q(status=1)&Q(secrete=0))
            else:
                papers = Paper.objects.filter(Q(cid=cid)&Q(status=1))
            papers = papers[start : start + 10]
            ret = ''
            for p in papers:
                if p.is_jump == 0:
                    ret += u"""<div class="list-arc-item "><a href="/blog/paper_detail/?pid=%s" title="%s"><div class="list-box"><h3>%s</h3><div class="info">%s</div></div></a><div class="tags font-ei "><i class="fa fa-lemon-o" title="tag：%s" data-toggle="tooltip"> %s</i>&nbsp;<i class="fa fa-clock-o" title="time：%s" data-toggle="tooltip" > %s</i>&nbsp;<i class="fa fa-commenting-o" title="comment：%s" data-toggle="tooltip" > %s</i>&nbsp;<i class="fa fa-thumbs-o-up" title="like：%s" data-toggle="tooltip" > %s</i>&nbsp;</div></div><hr>""" % (p.id, p.title, p.title, p.description, p.category, p.category, p.data, p.data, p.comment_total, p.comment_total, p.like, p.like)
                else:
                    ret += u"""<div class="list-arc-item "><a href="%s" title="%s" target="_blank"><div class="list-box"><h3>%s</h3><div class="info">%s</div></div></a><div class="tags font-ei "><i class="fa fa-lemon-o" title="tag：%s" data-toggle="tooltip"> %s</i>&nbsp;<i class="fa fa-clock-o" title="time：%s" data-toggle="tooltip" > %s</i>&nbsp;<i class="fa fa-commenting-o" title="comment：%s" data-toggle="tooltip" > %s</i>&nbsp;<i class="fa fa-thumbs-o-up" title="like：%s" data-toggle="tooltip" > %s</i>&nbsp;</div></div><hr>""" % (p.jumplink, p.title, p.title, p.description, p.category, p.category, p.data, p.data, p.comment_total, p.comment_total, p.like, p.like)
            status = [1, 0][len(papers) == 0]
            return HttpResponse(json.dumps({
                        "status": status,
                        "info": ret
                    })) 
    error = 'oops,没有找到资源。。。。。。。'
    return render_to_response('blog/error/404.html',{'error':error})


def paper_detail(request):
    if request.method == "GET":
        pid = request.GET.get('pid', '')
        p = getObject(Paper, id=pid)
        if p:
            if p.status == 0:
                error = '404, 该资源无法查看'
                return render_to_response('blog/error/404.html',{'error':error})
            if p.secrete == 1:
                if request.session.get('role_id', '') != 0:
                    error = '该内容需要登录才能查看'
                    return render_to_response('blog/login.html',{'error':error})
            p.views += 1
            p.save()
            ip = get_client_ip(request)
            try:
                uid = request.COOKIES.get('uid',-1)
                ret = get_area(ip)
                agent = request.META.get('HTTP_USER_AGENT','')
                _,agent = get_client_type(agent)
                if ret.get('status', 1) == 0:
                    view_log = Viewlog(uid=uid, ip=ip, pid=pid,lon=ret['content']['point']['x'], lat=ret['content']['point']['y'], agent=agent, province=ret['content']['address_detail']['province'],city=ret['content']['address_detail']['city'])
                    view_log.save()
            except:
                pass
            comments = Comment.objects.filter(Q(pid=pid)&Q(pcid=-1)&Q(status=1))[:10]
            if request.session.get('role_id', 1) == 0:
                preview_show = preview(pid, 1)
            else:
                preview_show = preview(pid, 0)
            return render_to_response('blog/paper/paper_detail.html', locals(), context_instance=RequestContext(request))
    elif request.method == "POST":
        pid = request.POST.get('id', '')
        page = request.POST.get('page', '')
        p = getObject(Paper, id=pid)
        if p:
            if p.status == 0:
                error = '404, 该资源无法查看'
                return render_to_response('blog/error/404.html',{'error':error})
            if p.secrete == 1:
                if request.session.get('role_id', '') != 0:
                    error = '该内容需要登录才能查看'
                    return render_to_response('blog/login.html',{'error':error})
            start = (int(page) - 1) * 10
            comments = Comment.objects.filter(Q(pid=pid)&Q(pcid=-1)&Q(status=1))[start : start + 10]
            ret = ''
            for c in comments:
                user_info = getObject(Users, id=c.uid)
                ruser_info = getObject(Users, id=c.ruid)
                user_login = request.session.get('user_id', False)
                ret += u"""<div class="box-comment"><img src="%s" alt="%s" class="img-circle img-md""><div class="comment-text"><span  class="username"><a href="#" target="_blank">%s</a><span class="text-muted pull-right"><i class="fa fa-clock-o"></i> %s</span></span>%s""" % (user_info.profile, user_info.profile, user_info.username, c.data, c.content)

                if user_login:
                    ret += u"""<br><div class=""><a href="javascript:void(0);" data-ruid="%s" data-pcid="%s" class="arc-btn pull-right"><i class="fa fa-mail-reply "></i>回复</a></div>""" % (c.uid, c.id)
                if is_reply(c.id) == 1:
                    ret += "<hr>"

                for r in reply(c.id):
                    if r != 0:
                        user = getObject(Users, id=r.uid)
                        ruser = getObject(Users, id=r.ruid)
                        ret += u"""<div class="box-comment"><img src="%s" alt="%s"  class="img-circle img-md"><div class="comment-text"><span  class="username"><a href="#" target="_blank">%s</a><span class="text-muted pull-right"><i class="fa fa-clock-o">%s</i></span></span>""" % (user.profile, user.profile, user.username, r.data)

                        if reply_user(r.id, c.uid) == 1:
                            ret += """<a href="#" class="font-blue">@%s</a><br>""" % ruser.username

                        ret += r.content + "</div>"

                        if user_login:
                            ret += """<div class=""><a href="javascript:void(0);" data-ruid="%s" data-pcid="%s" class="arc-btnpull-right"><i class="fa fa-mail-reply "></i>回复</a></div>""" % (r.uid, c.id)
                        ret += "</div>"
                ret += "</div>" + "</div>"

            status = [1, 0][len(comments) == 0]
            return HttpResponse(json.dumps({
                        "status": status,
                        "info": ret
                    })) 
    error = '没有找到资源。。。。。。。'
    return render_to_response('blog/error/404.html',{'error':error})


def blog_category_list(request):
    if request.session.get('role_id', '') == 0:
        cate = Category.objects.filter(status=1)
        papers = Paper.objects.filter(status=1)
    else:
        cate = Category.objects.filter(Q(status=1)&Q(secrete=0))
        papers = Paper.objects.filter(Q(status=1)&Q(secrete=0))
    paper_total = len(papers) 
    return render_to_response('blog/category/blog_category_list.html', locals(), context_instance=RequestContext(request))


def blog_search(request):
    if request.method == "GET":
        k = request.GET.get('k', '')
        if request.session.get('role_id', '') == 0:
            papers = Paper.objects.filter(
                Q(status=1)&
                (Q(title__contains=k)|
                Q(keywords__contains=k)|
                Q(description__contains=k)|
                Q(author__contains=k)|
                Q(content__contains=k))
                )
        else:
            papers = Paper.objects.filter(
                Q(status=1)&
                Q(secrete=0)&
                ((Q(title__contains=k)|
                Q(keywords__contains=k)|
                Q(description__contains=k)|
                Q(author__contains=k)|
                Q(content__contains=k)))
                )
        for p in papers:
            p.title = p.title.replace(k, u'<strong class="font-red">' + k + u'</strong>')
            p.description = p.description.replace(k, u'<strong class="font-red">' + k + u'</strong>')
        total = len(papers)
        return render_to_response('blog/public/search.html', locals(), context_instance=RequestContext(request))


def blog_thumbs(request):
    if request.method == "GET":
        pid = request.GET.get('id', '')
        paper = getObject(Paper, id=pid)
        kind = request.GET.get('kind', '')
        uid = request.COOKIES.get('uid', -1)
        ip = get_client_ip(request)
        try:
            if int(kind) == 0:
                thumb = Thumbs.objects.filter(Q(pid=pid)&Q(uid=uid)&Q(ip=ip)&Q(is_dislike=1))
                if thumb:
                    info = "为什么要点两次...."
                else:
                    agent = request.META.get('HTTP_USER_AGENT','')
                    _,agent = get_client_type(agent)
                    thumb = Thumbs(uid=uid, ip=ip, pid=pid, is_dislike=1, agent=agent)
                    thumb.save()
                    paper.dislike += 1
                    paper.save()
                    info = "emmmmmmmmmmm...."
            else:
                thumb = Thumbs.objects.filter(Q(pid=pid)&Q(ip=ip)&Q(uid=uid)&Q(is_dislike=0))
                if thumb:
                    info = '赞一次就吼了'
                else:    
                    agent = request.META.get('HTTP_USER_AGENT','')
                    thumb = Thumbs(uid=uid, ip=ip, pid=pid, agent=agent)
                    thumb.save()
                    paper.like += 1
                    paper.save()
                    info = "谢谢你的支持"
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
        txt = [" ","\t","\r\n"]
        rep = ["&nbsp;","&nbsp;&nbsp;&nbsp;&nbsp;","<br>","<br>"]
        for i in range(len(txt)):
            content = content.replace(txt[i], rep[i])

        create_time = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        comment = Comment(pid=pid, uid=uid, ruid=ruid, pcid=pcid, content=content,data=create_time)
        comment.save()
        ruser = getObject(Users, id=ruid)
        user = getObject(Users, id=uid)
        mail = getObject(Emailsetting, status=1)
        if mail:
            paper = getObject(Paper, id=pid)
            paper.comment_total += 1
            paper.save()

            config = Config.objects.all()
            if config:
                message_header = config[0].title
            else:
                message_header = WEB_TITLE
            mail_message = u"""
            <p> %s 回复你了 </p>
            <p> %s... </p>
            点击查看<a href="%s/blog/paper_detail/?pid=%s"> %s </a>
            """ % (user.username, content[:20], WEB_URL, pid, paper.title)
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

def request_error(request):
    error = "emmmmm, URL地址错误"
    return render_to_response('blog/error/404.html',{'error':error})


def preview(par,nums=None):
    par, nums = int(par), int(nums)
    paper = getObject(Paper, id=par)
    if nums == 1:
        # 可以看到隐私
        if paper:
            # 又是一个bug date写成data了
            left = Paper.objects.filter(Q(id__lt=paper.id)&Q(status=1)&Q(is_jump=0)).order_by('id')
            right = Paper.objects.filter(Q(id__gt=paper.id)&Q(status=1)&Q(is_jump=0)).order_by('id')
    elif nums == 0:
        if paper:
            left = Paper.objects.filter(Q(id__lt=paper.id)&Q(status=1)&Q(secrete=0)&Q(is_jump=0)).order_by('id')
            right = Paper.objects.filter(Q(id__gt=paper.id)&Q(status=1)&Q(secrete=0)&Q(is_jump=0)).order_by('id')
    if left:
        left_paper = u"""<a href="/blog/paper_detail/?pid=%s"><i class="fa fa-chevron-left"></i>%s</a>""" % (left[0].id, left[0].title)
    else:
        left_paper = u"""<span><i class="fa fa-exclamation"></i>到头了</span>"""
    if right:
        right_paper = u"""<a href="/blog/paper_detail/?pid=%s">%s<i class="fa fa-chevron-right"></i></a>""" % (right[0].id, right[0].title)
    else:
        right_paper = u"""<span><i class="fa fa-exclamation"></i>到底了</span>"""
    return u"""<span class="pull-left">%s</span><span class="pull-right">%s</span>""" % (left_paper, right_paper)