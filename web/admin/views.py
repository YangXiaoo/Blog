# coding:UTF-8
from __future__ import division 
import uuid 
import urllib
import time
import json

from django.db.models import Count
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseNotFound
from django.http import HttpResponse
from django.db.models import Q

from myweb.api import *
from myweb.models import *
from myweb.settings import *

from api import *

import ConfigParser

WEB_URL = 'http://www.lxa.kim'


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
                if userinfo.is_active == 1 and userinfo.password == password and userinfo.is_admin == 1:
                    request.session['role_id'] = 0
                    request.session.set_expiry(3600)
                    response = render_to_response(reverse('admin_index'), {})
                    return response
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
    request.session['role_id'] = ''
    return HttpResponseRedirect(reverse('admin_login'))


@admin_require_login
def admin_index(request):
    '''
    主页
    '''
    return render_to_response('admin/admin_index.html', locals(), context_instance=RequestContext(request))


def category_list(request):
    """
    文章分类
    """
    cate_find = Category.objects.all()
    cate_list, p, cate, page_range, current_page, show_first, show_end = pages(cate_find, request)
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
        cid = request.GET.get('id', '')
        c = getObject(Category, id=cid)
        try:
            papers = Paper.objects.filter(cid=cid)
            for p in papers:
                p.delete()
            c.delete()
            status = 1
            info = 'delete success!'
        except:
            status = 0
            info = 'fail'
        return HttpResponse(json.dumps({
                    "status": status,
                    "info": info
                })) 


def paper_list(request):
    papers_find = Paper.objects.all()
    paper_list, p, papers, page_range, current_page, show_first, show_end = pages(papers_find, request)
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
        pid = request.GET.get('id', '')
        p = getObject(Paper, id=pid)
        try:
            category = getObject(Category, id=p.cid)
            category.paper_total -= 1
            category.save()
            p.delete()
            status = 1
            info = 'delete success!'
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


def user_list(request):
    user_find = Users.objects.all()
    user_list, p, users, page_range, current_page, show_first, show_end = pages(user_find, request)
    return render_to_response('admin/user/user_list.html', locals(), context_instance=RequestContext(request))


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
        return HttpResponse(json.dumps({
        "status": status,
        "url" : '',
        "info":info,
        }))
    return render_to_response('admin/user/user_add.html', locals(), context_instance=RequestContext(request))


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


def user_del(request):
    if request.method == "GET":
        uid = request.GET.get('id', '')
        u = getObject(Users, id=uid)
        try:
            u.delete()
            status = 1
            info = 'delete successful!'
        except:
            status = 0
            info = 'fail'
        return HttpResponse(json.dumps({
                    "status": status,
                    "info": info
                })) 


def paper_comment_list(request):
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
        c.content = request.POST.get('content', '')
        c.status = request.POST.get('status', '')
        c.save()
        return HttpResponseRedirect(reverse('paper_comment_list'))


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


def comment_del(request):
    if request.method == "GET":
        cid = request.GET.get('id', '')
        c = getObject(Comment, id=cid)
        try:
            c.delete()
            status = 1
            info = 'delete successful!'
        except:
            status = 0
            info = 'fail'
        return HttpResponse(json.dumps({
                    "status": status,
                    "info": info
                })) 


def blog_message_list(request):
    pass


def web_config(request):
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


def web_file(request):
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


def web_file_del(request):
    if request.method == "GET":
        fid = request.GET.get('id', '')
        f = getObject(UpFiles, id=fid)
        try:
            f.delete()
            status = 1
            info = 'delete successful!'
        except:
            status = 0
            info = 'fail'
        return HttpResponse(json.dumps({
                    "status": status,
                    "info": info
                })) 


def login_log_list(request):
    find = Loginlog.objects.all()
    log_list, p, logs, page_range, current_page, show_first, show_end = pages(find, request)
    return render_to_response('admin/webmaster/login_log_list.html', locals(), context_instance=RequestContext(request))


def login_del(request):
    if request.method == "GET":
        fid = request.GET.get('id', '')
        f = getObject(Loginlog, id=fid)
        try:
            f.delete()
            status = 1
            info = 'delete successful!'
        except:
            status = 0
            info = 'fail'
        return HttpResponse(json.dumps({
                    "status": status,
                    "info": info
                }))  


def view_log_list(request):
    find = Viewlog.objects.all()
    papers = Paper.objects.all()
    for f in find:
        for p in papers:
            if f.pid == p.id:
                f.paper = p.title
    view_list, p, views, page_range, current_page, show_first, show_end = pages(find, request)
    return render_to_response('admin/webmaster/view_log_list.html', locals(), context_instance=RequestContext(request))


def view_log_del(request):
    if request.method == "GET":
        fid = request.GET.get('id', '')
        f = getObject(Viewlog, id=fid)
        try:
            f.delete()
            status = 1
            info = 'delete successful!'
        except:
            status = 0
            info = 'fail'
        return HttpResponse(json.dumps({
                    "status": status,
                    "info": info
                }))  


def blogroll_list(request):
    find = Blogroll.objects.all()
    roll_list, p, rolls, page_range, current_page, show_first, show_end = pages(find, request)
    return render_to_response('admin/webmaster/blogroll_list.html', locals(), context_instance=RequestContext(request))


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


def blogroll_del(request):
    if request.method == "GET":
        fid = request.GET.get('id', '')
        f = getObject(Blogroll, id=fid)
        try:
            f.delete()
            status = 1
            info = 'delete successful!'
        except:
            status = 0
            info = 'fail'
        return HttpResponse(json.dumps({
                    "status": status,
                    "info": info
                }))  

def database_list(request):
    files = UpFiles.objects.filter(typeid=2)
    files_list, p, files, page_range, current_page, show_first, show_end = pages(files, request)
    return render_to_response('admin/database/database_list.html', locals(), context_instance=RequestContext(request))


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
            size = bash('du -b %s' % file_path).split(' ')[0]
            up_file = UpFiles(typeid=2, file_name=file_name,file_path=file_dir, dirs=file_path, size=size)
            up_file.save()
        except:
            pass
    else:
        pass
    return HttpResponseRedirect(reverse('database_list'))


def database_recover(request):
    if request.method == "GET":
        fid = request.GET.get('id', '')
        f = getObject(UpFiles, id=fid)
        try:
            config = ConfigParser.ConfigParser()
            config.read(os.path.join(BASE_DIR, 'myweb.conf'))
            if config.get('db', 'engine') == 'mysql': 
                ret = bash('mysqldump   -u %s  -p %s  %s < %s' % (DB_USER,DB_PASSWORD, DB_DATABASE, file_path))
                if ret != 0:
                    ret = bash('mysql %s < %s' % (DB_DATABASE, f.file_path))
                status = 1
                info = 'database recover successful!'
            else:
                pass
        except:
            status = 0
            info = 'fail'
        return HttpResponse(json.dumps({
                    "status": status,
                    "info": info
                })) 