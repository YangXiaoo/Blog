# coding:UTF-8
# 2018-11-28 - 2018-12- 
import uuid 
import time,datetime, os
import json

from django.db.models import Count
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseNotFound
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.db.models import Q

from myweb.api import *
from myweb.models import *
from myweb.settings import *

from api import *

import ConfigParser
from email.mime.text import MIMEText
from email.header import Header

# import markdown

WEB_URL = 'http://yangxiao.online'
WEB_TITLE = '杨潇-博客'
OLD_URL = 'www.lxa.kim'

@defendAttack
def admin_login(request):
    error = ''
    if request.method == 'GET':
        return render_to_response('admin/login.html')
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            userinfo = getObject(Users, username=username)
            if userinfo is not None:
                if userinfo.is_active == 1 :
                    if  userinfo.password == password :
                        if userinfo.is_admin == 1:
                            try:
                                agent = request.META.get('HTTP_USER_AGENT','')
                                ip = get_client_ip(request)
                                ret = get_area(ip)
                                if ret.get('status', 1) == 0:
                                    login_log = Loginlog(uid=userinfo.id, name=userinfo.username, ip=ip, province=ret['content']['address_detail']['province'],city=ret['content']['address_detail']['city'],district=ret['content']['address_detail']['district'],lon=ret['content']['point']['x'], lat=ret['content']['point']['y'], agent=agent)
                                    login_log.save()
                            except:
                                pass
                            request.session['role_id'] = 0
                            request.session['uid'] = userinfo.id
                            request.session.set_expiry(3600)
                            response= HttpResponseRedirect(reverse('admin_index'))
                            response.set_cookie('profile',userinfo.profile)
                            response.set_cookie('username',userinfo.username)
                            return response
                        else:
                            error = '不是管理员'
                    else:
                        error = '密码错误'
                else:
                    error = '用户未激活'
            else:
                error = '用户不存在'
        else:
            error = '用户名或密码未正确输入'
    return render_to_response('admin/login.html',{'error':error})



@admin_require_login
def admin_logout(request):
    '''
    注销
    '''
    response = HttpResponseRedirect(reverse('admin_login'))
    try:
        del request.session['role_id']
        del request.session['uid']
        response.delete_cookie('username')
        response.delete_cookie('profile')
    except:
        pass
    return response


@common
def admin_index(request):
    '''
    主页
    '''
    set_view(request)
    papers = Paper.objects.all()
    paper_total = len(papers)

    view_log = Viewlog.objects.all()
    view_total = len(view_log)

    users = Users.objects.all()
    user_total = len(users)

    like = Thumbs.objects.filter(is_dislike=0)
    like_total = len(like)
    # dt_s= datetime.datetime.now()
    # dt_e = (dt_s - datetime.timedelta(30))
    # like_new = Thumbs.objects.filter(Q(date__range=[dt_s, dt_e])&Q(is_dislike=0))
    # dt_s = (dt_e - datetime.timedelta(30))
    # like_old = Thumbs.objects.filter(Q(date__range=[dt_e, dt_s])&Q(is_dislike=0))
    # like_increase = like_new // like_old * 100
    dislike = Thumbs.objects.filter(is_dislike=1)
    dislike_total = len(dislike)

    comments = Comment.objects.all()
    comments_total = len(comments)

    # login stastics
    now = datetime.datetime.now()
    start = now - datetime.timedelta(days=30)

    login_log = Loginlog.objects.filter(date__gt=start)  

    login_line_x, login_line_y = [], []
    dicts = {}
    for l in login_log:
        login_time = l.date.strftime('%Y-%m-%d')
        dicts[login_time] = dicts.get(login_time, 0) + 1
    sorts = sorted(dicts.items(), key=lambda x:x[0])
    for k, v in sorts:
        login_line_x.append(k)
        login_line_y.append(v)

    login_line_x, login_line_y = json.dumps(login_line_x), json.dumps(login_line_y)

    # paper view stastics
    view_log = Viewlog.objects.filter(date__gt=start)   
    paper_view_line_x, paper_view_line_y = [], []
    dicts = {}
    for v in view_log:
        view_time = v.date.strftime('%Y-%m-%d')
        dicts[view_time] = dicts.get(view_time, 0) + 1
    sorts = sorted(dicts.items(), key=lambda x:x[0])
    for k, v in sorts:
        paper_view_line_x.append(k)
        paper_view_line_y.append(v)

    paper_view_line_x, paper_view_line_y = json.dumps(paper_view_line_x), json.dumps(paper_view_line_y)

    # user active stastics
    views = Viewlog.objects.all()
    user_active_data = []
    value = {}
    corrdinate = {}
    for v in views:
        value[v.city] = value.get(v.city, 0) + 1
        if v.city not in corrdinate:
            corrdinate[v.city] = [v.lon, v.lat]
    for k, v in corrdinate.items():
        if k:
            tmp = {}
            tmp['name'] = k 
            v.append(value.get(k))
            tmp['value'] = v
            user_active_data.append(tmp)
    max_view = 0
    for k,v in value.items():
        if v > max_view:
            max_view = v
    # user_active_data.append({'name':'云浮市', 'value':[112.05094596,22.93797569,40]})
    user_active_data = json.dumps(user_active_data)

    # recent login log stastics
    last_login =  Loginlog.objects.all().order_by('-date')[:10]

    # user agent type stastics
    data = {}
    brower_title, brower_data = [], []
    for v in views:
        data[v.agent] = data.get(v.agent, 0) + 1
    for k,v in data.items():
        tmp = {}
        tmp['name'] = k
        tmp['value'] = v
        brower_data.append(tmp)
        brower_title.append(k)
    brower_data, brower_title = json.dumps(brower_data), json.dumps(brower_title)

    return render_to_response('admin/admin_index.html', locals(), context_instance=RequestContext(request))


@common
def category_list(request):
    """
    文章分类
    """
    set_view(request)
    cate_find = Category.objects.all()
    cate_list, p, cate, page_range, current_page, show_first, show_end = pages(cate_find, request)
    return render_to_response('admin/category/category_list.html', locals(), context_instance=RequestContext(request))


@admin_require_login
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


@admin_require_login
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


@admin_require_login
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
            for p in papers:
                p.secrete = secrete
                p.save()
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

@admin_require_login
def category_del(request):
    if request.method == "POST":
        fid = request.POST.get('id', '')
        fid = fid.split(',')
        try:
            for k in fid:
                f = getObject(Viewlog, id=k)
                papers = Paper.objects.filter(cid=f.id)
                for p in papers:
                    p.delete()
                f.delete()
            status = 1
            info = 'delete successful!'
        except Exception as e:
            status = 0
            info = str(e)
        return HttpResponse(json.dumps({
                    "status": status,
                    "info": info
                })) 

@common
def paper_list(request):
    set_view(request)
    papers_find = Paper.objects.all()
    paper_list, p, papers, page_range, current_page, show_first, show_end = pages(papers_find, request)
    return render_to_response('admin/paper/paper_list.html', locals(), context_instance=RequestContext(request))


@admin_require_login
def paper_add(request):
    if request.method == "POST":
        cid = request.POST.get('typeid','')
        keys = ['title', 'tag', 'jumplink', 'litpic', 
            'content', 'author', 'source', 'keywords',
             'description', 'views', 'like', 'dislike',
              'status', 'secrete']
        data = {}
        for k in keys:
            data[k] = request.POST.get(k, '')
        for k in ['views', 'like', 'dislike']:
            data[k] = [data[k], 0][data[k] == '']
        create_time = request.POST.get('create_time')
        if create_time == '':
            create_time = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        category = getObject(Category, id=cid).category_name
        if len(data['jumplink']) > 5:
            is_jump = 1
        else:
            is_jump = 0
        paper = Paper(cid=cid, category=category, data=create_time,is_jump=is_jump, **data)
        paper.save()
        category = getObject(Category, id=cid)
        category.paper_total += 1
        category.save()
        return HttpResponseRedirect(reverse('paper_list'))
    elif request.method == "GET":
        cid = request.GET.get('cid', '')
    cate = Category.objects.all()
    return render_to_response('admin/paper/paper_add.html', locals(), context_instance=RequestContext(request))


@admin_require_login
def paper_push(request):
    if request.method == "POST":
        pid = request.POST.get('id', '')
        paper = getObject(Paper, id=pid)
        # send mail
        try:
            if paper.secrete == 0 and paper.status == 1:
                users = Users.objects.all()
                recivers = []
                for u in users:
                    recivers.append(u.email)
                mail = getObject(Emailsetting, status=1)
                config = Config.objects.all()
                if config:
                    message_header = config[0].title
                else:
                    message_header = WEB_TITLE
                mail_message = u"""<p> 快来围观！ </p><p> 有新文章发布了！</p><a href="%s/blog/paper_detail/?pid=%s"> %s </a>""" % (WEB_URL, pid, paper.title)
                message = MIMEText(mail_message, 'html', 'utf-8')
                message['From'] = Header(message_header, 'utf-8')
                message['To'] = '求围观'
                subject = '有新文章发布~'
                message['Subject'] = Header(subject, 'utf-8')
                send_mail(mail, recivers, message.as_string())
                status = 1
                info = '推送成功'
            elif paper.secrete == 1:
                info = '文章为隐私状态, 无法推送'
                status = 0
            elif paper.status == 0:
                info = '文章暂停使用, 无法推送'
                status = 0
        except Exception as e:
            status = 0
            info = str(e)
        return HttpResponse(json.dumps({
                    "status": status,
                    "info": info
                })) 


@admin_require_login
def paper_edit(request):
    if request.method == "POST":
        # 待简化
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
        if len(jumplink) > 5:
            is_jump = 1
        else:
            is_jump = 0
        data = request.POST.get('create_time',time.strftime('%Y-%m-%d',time.localtime(time.time())))
        paper = getObject(Paper, id=id)
        Paper.objects.filter(id=id).update(cid=cid, category=category, title=title, tag=tag, jumplink=jumplink,litpic=litpic, content=content, author=author, source=source, keywords=keywords, description=description, views=views, like=like, dislike=dislike, status=status, data=data, is_jump=is_jump)
        return HttpResponseRedirect(reverse('paper_list'))
    elif request.method == "GET":
        pid = request.GET.get('pid', '')
        p = getObject(Paper, id=pid)
        cate = Category.objects.all()
        return render_to_response('admin/paper/paper_edit.html', locals(), context_instance=RequestContext(request))


@admin_require_login
def paper_edit_inline(request):
    if request.method == "GET":
        pid = request.GET.get('id', )
        name = request.GET.get('name', '')
        status = request.GET.get('status','')
        secrete = request.GET.get('secrete', '')
    elif request.method == "POST":
        pid = request.POST.get('id', )
        name = request.POST.get('name', '')
        status = request.POST.get('status','')
        secrete = request.POST.get('secrete', '')
    paper = getObject(Paper, id=pid)

    try:
        if status != '':
            paper.status = status
        elif name != '':
            paper.title = name
        elif secrete != '':
            paper.secrete = secrete
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


@admin_require_login
def paper_del(request):
    if request.method == "POST":
        fid = request.POST.get('id', '')
        fid = fid.split(',')
        try:
            for k in fid:
                f = getObject(Paper, id=k)
                category = getObject(Category, id=f.cid)
                category.paper_total -= 1
                category.save()
                f.delete()
            status = 1
            info = 'delete successful!'
        except Exception as e:
            status = 0
            info = str(e)
        return HttpResponse(json.dumps({
                    "status": status,
                    "info": info
                })) 


@common
def email_setting(request):
    set_view(request)
    if EMAIL_HOST_PASSWORD:
        if not getObject(Emailsetting, password=EMAIL_HOST_PASSWORD):
            try:
                email = Emailsetting(host=EMAIL_HOST, port=EMAIL_PORT, user=EMAIL_HOST_USER, password=EMAIL_HOST_PASSWORD, status=int(MAIL_ENABLE))
                email.save()
            except:
                pass
    emails = Emailsetting.objects.all()
    email_list, p, email, page_range, current_page, show_first, show_end = pages(emails, request)
    return render_to_response('admin/config/email_setting.html', locals(), context_instance=RequestContext(request)) 


@admin_require_login
def email_test(request):
    if request.method == "POST":
        eid = request.POST.get('id', '')
        e = getObject(Emailsetting, id=eid)
        try:
            if test_mail(e):
                status = 1
                info = 'email test successful!'
            else:
                status = 0
                info = 'fail'
        except Exception as e:
            status = 0
            info = 'fail' + '<br>' + str(e)
        return HttpResponse(json.dumps({
                    "status": status,
                    "info": info
                })) 


@admin_require_login
def email_add(request):
    if request.method == "POST":
        keys = ['host', 'port', 'user', 'password', 'status', 'description']
        data = {}
        for k in keys:
            data[k] = request.POST.get(k, '')
        email = Emailsetting(**data)
        email.save()
        return HttpResponseRedirect(reverse('email_setting'))
    return render_to_response('admin/config/email_add.html')


@admin_require_login
def email_edit(request):
    if request.method == "GET":
        eid = request.GET.get('id', '')
        email = getObject(Emailsetting, id=eid)
        return render_to_response('admin/config/email_edit.html', locals(), context_instance=RequestContext(request))
    elif request.method == "POST":
        eid = request.POST.get('id', '')
        try:
            keys = ['host', 'port', 'user', 'password', 'status', 'description']
            data = {}
            for k in keys:
                data[k] = request.POST.get(k, '')
            Emailsetting.objects.filter(id=eid).update(**data)
        except:
            pass
        return HttpResponseRedirect(reverse('email_setting'))


@admin_require_login
def email_edit_inline(request):
    if request.method == "POST":
        eid = request.POST.get('id', '')
        status = request.POST.get('status', '')
        email = getObject(Emailsetting, id=eid)
        try:
            email.status = status
            email.save()
            status = 1
            info = 'ok'
        except:
            status = 0
            info = 'fail'
        return HttpResponse(json.dumps({
                    "status": status,
                    "info": info
                })) 


@admin_require_login
def email_del(request):
    if request.method == "POST":
        fid = request.POST.get('id', '')
        fid = fid.split(',')
        try:
            for k in fid:
                f = getObject(Emailsetting, id=k)
                f.delete()
            status = 1
            info = 'delete successful!'
        except Exception as e:
            status = 0
            info = str(e)
        return HttpResponse(json.dumps({
                    "status": status,
                    "info": info
                })) 

@admin_require_login
def test(request):
    if request.method == "POST":
        pass
    return render_to_response('admin/test.html', locals(), context_instance=RequestContext(request))


@admin_require_login
def admin_markdown_upload_image(request):
    upload_files = request.FILES.getlist('editormd-image-file', None)
    date_now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    upload_dir, filename_path = get_tmp_dir()
    try:
        url = ''
        for upload_file in upload_files:
            file_path = '%s/%s' % (upload_dir, upload_file.name)
            file_dir = '%s/%s' % (filename_path, upload_file.name)
            size = upload_file.size
            up_file = UpFiles(file_name=upload_file.name,file_path=file_dir, dirs=file_path, size=size)
            up_file.save()
            with open(file_path,'w') as f:
                for chunk in upload_file.chunks():
                    f.write(chunk)
            url = WEB_URL + file_path.split(BASE_DIR)[-1]
        message = WEB_URL + str(len(upload_files))
        success = 1
    except Exception as e:
        message = str(e) + str(upload_files)
        url = WEB_URL + 'callback_fail'
        success = 0
    return HttpResponse(json.dumps({
                "success": success,
                "url" : url,
                "message":message,
            }))    


@admin_require_login
def admin_upload_image(request):
    upload_files = request.FILES.getlist('imgFile', None)
    date_now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    upload_dir, filename_path = get_tmp_dir()
    try:
        url = ''
        for upload_file in upload_files:
            file_path = '%s/%s' % (upload_dir, upload_file.name)
            file_dir = '%s/%s' % (filename_path, upload_file.name)
            size = upload_file.size
            up_file = UpFiles(typeid=1, file_name=upload_file.name,file_path=file_dir, dirs=file_path, size=size)
            up_file.save()
            with open(file_path,'w') as f:
                for chunk in upload_file.chunks():
                    f.write(chunk)
            url = WEB_URL + file_path.split(BASE_DIR)[-1]
        info = "upload file successful!"
        success = 1
    except Exception as e:
        info = str(e)
        url = WEB_URL + 'callback_fail'
        success = 0
    return HttpResponse(json.dumps({
                "success": success,
                "url" : url,
                "info":info,
            }))


@admin_require_login
def admin_upload_file(request):
    upload_files = request.FILES.getlist('file', None)
    date_now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    upload_dir, filename_path = get_tmp_dir()
    try:
        url = ''
        for upload_file in upload_files:
            file_path = '%s/%s' % (upload_dir, upload_file.name)
            file_dir = '%s/%s' % (filename_path, upload_file.name)
            size = upload_file.size
            up_file = UpFiles(typeid=3, file_name=upload_file.name,file_path=file_dir, dirs=file_path, size=size)
            up_file.save()
            with open(file_path,'w') as f:
                for chunk in upload_file.chunks():
                    f.write(chunk)
            url = WEB_URL + file_path.split(BASE_DIR)[-1]
        info = "上传成功,刷新查看"
        success = 1
    except Exception as e:
        info = str(e)
        url = WEB_URL + 'callback_fail'
        success = 0
    return HttpResponse(json.dumps({
                "success": success,
                "url" : url,
                "info":info,
            }))


@common
def user_list(request):
    set_view(request)
    user_find = Users.objects.all()
    user_list, p, users, page_range, current_page, show_first, show_end = pages(user_find, request)
    return render_to_response('admin/user/user_list.html', locals(), context_instance=RequestContext(request))


@admin_require_login
def user_add(request):
    if request.method == "POST":
        username = request.POST.get('username','')
        password = request.POST.get('password','')
        repassword = request.POST.get('repassword','')
        if password != repassword:
            return HttpResponse(json.dumps({
            "status": 0,
            "url" : '',
            "info":'两次密码不一致',
            }))
        name = request.POST.get('name','')
        email = request.POST.get('email','')
        gender = request.POST.get('gender','')
        is_active = request.POST.get('status','')
        is_admin = request.POST.get('admin','')

        config = Config.objects.all()
        if config:
            profile = config[0].default_img
        else:
            profile = ''
        user = Users(username=username, password=password, name=name, email=email,profile=profile, gender=gender, is_active=is_active, is_admin=is_admin)
        try:
            user.save()
            status = 1
            info = 'successful!'
        except Exception as e:
            status = 0
            info = str(e)
        return HttpResponseRedirect(reverse('user_list'))
    return render_to_response('admin/user/user_add.html', locals(), context_instance=RequestContext(request))

@admin_require_login
def user_edit(request):
    if request.method == "POST":
        method = request.POST.get('actions','')
        uid = request.POST.get('id', '') 
        user = getObject(Users, id=uid)
        if method == 'baseinfo':        
            user.email = request.POST.get('email', '')
            user.gender = request.POST.get('gender')
        elif method == 'password':
            user.password = request.POST.get('password', '')
        elif method == 'avatar':
            # upload_files = request.FILES.getlist('imgFile', None)
            # date_now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            # upload_dir, filename_path = get_tmp_dir()
            # try:
            #     url = ''
            #     for upload_file in upload_files:
            #         file_path = '%s/%s' % (upload_dir, upload_file.name)
            #         file_dir = '%s/%s' % (filename_path, upload_file.name)
            #         size = upload_file.size
            #         up_file = UpFiles(typeid=1, file_name=upload_file.name,file_path=file_dir, dirs=file_path, size=size)
            #         up_file.save()
            #         with open(file_path,'w') as f:
            #             for chunk in upload_file.chunks():
            #                 f.write(chunk)
            #         url = WEB_URL + file_path.split(BASE_DIR)[-1]
            user.profile = request.POST.get('avatar', '')
            # return HttpResponse(json.dumps({
            #             "success": success,
            #             "url" : url,
            #             "info":info,
            #         }))
        elif method == 'infos':
            user.user_info = request.POST.get('info', ''
                )
        try:
            user.save()
            status = 1
            info = 'successful!'
        except Exception as e:
            status = 0
            info = str(e)
        return HttpResponse(json.dumps({
        "status": status,
        "url" : '',
        "info":info,
        }))

    elif request.method == "GET":
        uid = request.GET.get('id', '')
        u = getObject(Users, id=uid)
        return render_to_response('admin/user/user_edit.html', locals(), context_instance=RequestContext(request))


@admin_require_login
def user_edit_inline(request):
    if request.method == "GET":
        uid = request.GET.get('id', )
        name = request.GET.get('name', '')
        active = request.GET.get('active','')
        admin = request.GET.get('admin','')
    elif request.method == "POST":
        uid = request.POST.get('id', )
        name = request.POST.get('name', '')
        active = request.POST.get('active','')
        admin = request.POST.get('admin','')
    user = getObject(Users, id=uid)
    try:
        if name != '':
            user.name = name
        elif active != '':
            user.is_active = active
        elif admin != '':
            user.is_admin = admin
        user.save()
        status = 1
        info = 'successful!'
    except:
        status = 0
        info = 'fail'
    return HttpResponse(json.dumps({
                "status": status,
                "info": info
            })) 

@admin_require_login
def user_del(request):
    if request.method == "POST":
        fid = request.POST.get('id', '')
        fid = fid.split(',')
        try:
            for k in fid:
                f = getObject(Users, id=k)
                f.delete()
            status = 1
            info = 'delete successful!'
        except Exception as e:
            status = 0
            info = str(e)
        return HttpResponse(json.dumps({
                    "status": status,
                    "info": info
                })) 

@common
def paper_comment_list(request):
    set_view(request)
    find = Comment.objects.all()
    papers = Paper.objects.all()
    users = Users.objects.all()
    for f in find:
        for p in papers:
            if f.pid == p.id:
                f.title = p.title
        for u in users:
            if f.uid == u.id:
                f.user = u.username 
            if f.ruid == u.id:
                f.ruser = u.username

    comment_list, p, comments, page_range, current_page, show_first, show_end = pages(find, request)
    return render_to_response('admin/comment/paper_comment_list.html', locals(), context_instance=RequestContext(request))

@admin_require_login
def comment_edit(request):
    if request.method == "GET":
        cid = request.GET.get('id', '')
        c = getObject(Comment, id=cid)
        paper = getObject(Paper, id=c.pid)
        user = getObject(Users, id=c.uid)
        ruser = getObject(Users, id=c.ruid)
        rc = getObject(Comment, id=c.pcid)
        return render_to_response('admin/comment/comment_edit.html', locals(), context_instance=RequestContext(request))
    elif request.method == "POST":
        cid = request.POST.get('id', '')
        c = getObject(Comment, id=cid)

        content = request.POST.get('content', '')
        txt = [" ","\t","\r\n"]
        rep = ["&nbsp;","&nbsp;&nbsp;&nbsp;&nbsp;","<br>","<br>"]
        for i in range(len(txt)):
            content = content.replace(txt[i], rep[i])
        c.content = content
        c.status = request.POST.get('status', '')
        c.save()
        return HttpResponseRedirect(reverse('paper_comment_list'))

@admin_require_login
def comment_edit_inline(request):
    if request.method == "GET":
        cid = request.GET.get('id', )
        status = request.GET.get('status', '')
    elif request.method == "POST":
        cid = request.POST.get('id', )
        status = request.POST.get('status', '')
    c = getObject(Comment, id=cid)
    try:
        c.status = status
        c.save()
        status = 1
        info = 'successful!'
    except:
        status = 0
        info = 'fail'
    return HttpResponse(json.dumps({
                "status": status,
                "info": info
            })) 


@admin_require_login
def comment_del(request):
    if request.method == "POST":
        fid = request.POST.get('id', '')
        fid = fid.split(',')
        try:
            for k in fid:
                f = getObject(Comment, id=k)
                paper = getObject(Paper, id=f.pid)
                paper.comment_total -= 1
                paper.save()
                f.delete()
            status = 1
            info = 'delete successful!'
        except Exception as e:
            status = 0
            info = str(e)
        return HttpResponse(json.dumps({
                    "status": status,
                    "info": info
                })) 


@admin_require_login
def blog_message_list(request):
    pass


@common
def web_config(request):
    set_view(request)
    if request.method == 'POST':
        id = request.POST.get('id', '') 
        key = ['title', 'keywords', 'description','copyright', 'web_logo', 'address', 'record', 'web_owner', 'default_img']
        data = {}
        for k in key:
            data[k] = request.POST.get(k, '')
        try:
            if id == '':
                config = Config(**data)
                config.save()
            else:
                Config.objects.filter(id=id).update(**data)
            user = Users.objects.all()
            for u in user:
                if not u.profile:
                    u.profile = data['default_img']
                    u.save()
            status = 1
            info = 'successful!'
        except Exception as e:
            status = 0
            info = str(e)
        return HttpResponse(json.dumps({
                    "status": status,
                    "info": info
                })) 
    web = Config.objects.all()
    if web:
        web = web[0]
    return render_to_response('admin/config/web_config.html', locals(), context_instance=RequestContext(request))


@admin_require_login
def web_file(request):
    set_view(request)
    files = UpFiles.objects.all()
    if request.method == "GET":
        keyword = request.GET.get('keyword', '')
        file_dir = request.GET.get('download', '')
        if file_dir:
            file_path = os.path.join(BASE_DIR, 'static/files', file_dir)
            if os.path.isfile(file_path):
                f = open(file_path)
                data = f.read()
                f.close()
                response = HttpResponse(data, content_type='application/octet-stream')
                response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(file_path)
                return response
    elif request.method == "POST":
        file_id = request.POST.get('id', '')
    if keyword:
        files = UpFiles.objects.filter(file_name__contains=keyword)
    files_list, p, files, page_range, current_page, show_first, show_end = pages(files, request)
    return render_to_response('admin/config/web_file.html', locals(), context_instance=RequestContext(request))


@admin_require_login
def file_edit_inline(request):
    if request.method == "GET":
        file_id = request.GET.get('id','')
        file_name = request.GET.get('name','')
    elif request.method == "POST":
        file_name = request.POST.get('name', '')
        file_id = request.POST.get('id','')
    else:
        return HttpResponse('Error request')
    file = getObject(UpFiles, id=file_id)
    file.file_name = file_name
    try:
        file.save()
        status = 1
        info = 'ok'
    except:
        status = 0
        info = 'fail'
    return HttpResponse(json.dumps({
                "status": status,
                "info": info
            })) 


@admin_require_login
def web_file_del(request):
    if request.method == "POST":
        fid = request.POST.get('id', '')
        fid = fid.split(',')
        try:
            for k in fid:
                f = getObject(UpFiles, id=k)
                f.delete()
            status = 1
            info = 'delete successful!'
        except Exception as e:
            status = 0
            info = str(e)
        return HttpResponse(json.dumps({
                    "status": status,
                    "info": info
                })) 

@common
def login_log_list(request):
    set_view(request)
    find = Loginlog.objects.all()
    log_list, p, logs, page_range, current_page, show_first, show_end = pages(find, request)
    return render_to_response('admin/webmaster/login_log_list.html', locals(), context_instance=RequestContext(request))


@admin_require_login
def login_del(request):  
    if request.method == "POST":
        fid = request.POST.get('id', '')
        fid = fid.split(',')
        try:
            for k in fid:
                f = getObject(Loginlog, id=k)
                f.delete()
            status = 1
            info = 'delete successful!'
        except Exception as e:
            status = 0
            info = str(e)
        return HttpResponse(json.dumps({
                    "status": status,
                    "info": info
                })) 

@common
def view_log_list(request):
    set_view(request)
    find = Viewlog.objects.all()
    papers = Paper.objects.all()
    for f in find:
        for p in papers:
            if f.pid == p.id:
                f.paper = p.title
    view_list, p, views, page_range, current_page, show_first, show_end = pages(find, request)
    return render_to_response('admin/webmaster/view_log_list.html', locals(), context_instance=RequestContext(request))


@admin_require_login
def view_log_del(request):
    if request.method == "POST":
        fid = request.POST.get('id', '')
        fid = fid.split(',')
        try:
            for k in fid:
                f = getObject(Viewlog, id=k)
                f.delete()
            status = 1
            info = 'delete successful!'
        except Exception as e:
            status = 0
            info = str(e)
        return HttpResponse(json.dumps({
                    "status": status,
                    "info": info
                })) 


@common
def blogroll_list(request):
    set_view(request)
    find = Blogroll.objects.all()
    roll_list, p, rolls, page_range, current_page, show_first, show_end = pages(find, request)
    return render_to_response('admin/webmaster/blogroll_list.html', locals(), context_instance=RequestContext(request))


@admin_require_login
def blogroll_add(request):
    if request.method == "POST":
        lists = ['web_name', 'web_link', 'web_logo', 'web_owner_email', 'web_description', 'sorts', 'status']
        data = {}
        for k in lists:
            data[k] = request.POST.get(k, '')
        try:
            r = Blogroll(**data)
            r.save()
            status = 1
            info = 'successful!'
        except Exception as e:
            status = 0
            info = str(e)
        return HttpResponse(json.dumps({
        "status": status,
        "url" : '',
        "info":info,
        }))

    return render_to_response('admin/webmaster/blogroll_add.html', locals(), context_instance=RequestContext(request))

@admin_require_login
def blogroll_edit(request):
    if request.method == "POST":
        rid = request.POST.get('id','')
        lists = ['web_name', 'web_link', 'web_logo', 'web_owner_email', 'web_description', 'sorts', 'status']
        data = {}
        for k in lists:
            data[k] = request.POST.get(k, '')
        try:
            Blogroll.objects.filter(id=rid).update(**data)
            status = 1
            info = 'successful!'
        except Exception as e:
            status = 0
            info = str(e)
        return HttpResponse(json.dumps({
        "status": status,
        "url" : '',
        "info":info,
        }))
    elif request.method == "GET":
        rid = request.GET.get('id', '')
        r = getObject(Blogroll, id=rid)
        return render_to_response('admin/webmaster/blogroll_edit.html', locals(), context_instance=RequestContext(request))


@admin_require_login
def blogroll_edit_inline(request):
    if request.method == "GET":
        rid = request.GET.get('id', )
        name = request.GET.get('name', '')
        status = request.GET.get('status','')
    elif request.method == "POST":
        rid = request.POST.get('id', )
        name = request.POST.get('name', '')
        status = request.POST.get('status','')
    blog = getObject(Blogroll, id=rid)
    try:
        if name != '':
            blog.name = name
        elif status != '':
            blog.status = status
        blog.save()
        status = 1
        info = 'successful!'
    except:
        status = 0
        info = 'fail'
    return HttpResponse(json.dumps({
                "status": status,
                "info": info
            })) 


@admin_require_login
def blogroll_del(request):
    if request.method == "POST":
        fid = request.POST.get('id', '')
        fid = fid.split(',')
        try:
            for k in fid:
                f = getObject(Blogroll, id=k)
                f.delete()
            status = 1
            info = 'delete successful!'
        except Exception as e:
            status = 0
            info = str(e)
        return HttpResponse(json.dumps({
                    "status": status,
                    "info": info
                })) 


@common
def database_list(request):
    set_view(request)
    files = UpFiles.objects.filter(typeid=2)
    files_list, p, files, page_range, current_page, show_first, show_end = pages(files, request)
    return render_to_response('admin/database/database_list.html', locals(), context_instance=RequestContext(request))


@admin_require_login
def database_backup(request):
    config = ConfigParser.ConfigParser()
    config.read(os.path.join(BASE_DIR, 'myweb.conf'))
    if config.get('db', 'engine') == 'mysql': 
        file_name = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S")) + '.sql'
        upload_dir, filename_path = get_tmp_dir()
        try:
            file_path = '%s/%s' % (upload_dir, file_name)
            file_dir = '%s/%s' % (filename_path, file_name)
            ret = bash('mysqldump   -u %s  -p %s  %s > %s' % (DB_USER,DB_PASSWORD, DB_DATABASE, file_path))
            if ret != 0:
                ret = bash('mysqldump  %s > %s' % (DB_DATABASE, file_path))
            size = os.popen('du -b %s' % file_path).readlines()[0].split('\t')[0]
            up_file = UpFiles(typeid=2, file_name=file_name,file_path=file_dir, dirs=file_path, size=size)
            up_file.save()
        except:
            error = '出错了'
    else:
        error = '暂时只支持mysql数据备份'
    return HttpResponseRedirect(reverse('database_list'))


@admin_require_login
def database_recover(request):
    if request.method == "POST":
        fid = request.POST.get('id', '')
        f = getObject(UpFiles, id=fid)
        try:
            config = ConfigParser.ConfigParser()
            config.read(os.path.join(BASE_DIR, 'myweb.conf'))
            if config.get('db', 'engine') == 'mysql': 
                ret = bash('mysqldump   -u %s  -p %s  %s < %s' % (DB_USER,DB_PASSWORD, DB_DATABASE, f.file_path))
                if ret != 0:
                    ret = bash('mysqldump %s < %s' % (DB_DATABASE, f.file_path))
                status = 1
                info = 'database recover successful!'
            else:
                info = '暂时只支持mysql数据库的还原'
                status = 0
        except Exception as e:
            status = 0
            info = str(e)
        return HttpResponse(json.dumps({
                    "status": status,
                    "info": info
                })) 


