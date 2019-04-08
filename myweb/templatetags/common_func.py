#!/usr/bin/python
# coding: utf-8
# 2018-11-27

from django import template
from django.utils.safestring import mark_safe
from django.db.models import Q

register = template.Library()
from admin.models import *
from myweb.models import *
from myweb.api import getObject

@register.filter
def get_config(par):
    config = Config.objects.all()
    if config:
        config = config[0]
        values = {  
            'title' : config.title,
            'keywords': config.keywords,
            'description' : config.description,
            'copyright' : config.copyright,
            'web_logo' : config.web_logo,
            'record' : config.record,
            'address' : config.address,
            'web_owner' : config.web_owner,
            'default_img' : config.default_img,
        }
        return values.get(par, '')
    return ''


@register.filter
def get_paper_img(pid):
    """返回文章封面"""
    paper = getObject(Paper, id=pid)
    if paper.litpic:
        return paper.litpic
    else:
        config = Config.objects.all()
        if config:
            return config[0].default_img

@register.filter
def category(par,nums):
    if nums == 0:
        cate = Category.objects.filter(Q(status=1)&Q(secrete=0)).order_by(str(par))
        for c in cate:
            papers = Paper.objects.filter((Q(status=0)|Q(secrete=1))&Q(cid=c.id))
            c.paper_total -= len(papers)
    elif nums == 1:
        cate = Category.objects.filter(status=1).order_by(str(par))
    else:
        cate = []
    if cate:
        start = 1
        for c in cate:
            c.sort = start
            start += 1
    return cate


@register.filter
def hot_paper(par,nums):
    if nums == 1:
        p = Paper.objects.filter(status=1).order_by(str(par))[: 5]
    elif nums == 0:
        p = Paper.objects.filter(Q(status=1)&Q(secrete=0)).order_by(str(par))[: 5]
    else:
        p = []
    if p:
        s = 1
        for x in p:
            x.sort = s
            s += 1
    return p


@register.filter
def paper_list(par,uid=None):
    uid = int(uid)
    if uid == 0:
        p = Paper.objects.filter(Q(cid=int(par))&Q(status=1))
    elif uid == 1:
        p = Paper.objects.filter(Q(cid=int(par))&Q(secrete=0)&Q(status=1))
    else:
        p = ''
    return p


@register.filter
def preview(par,nums=None):
    par, nums = int(par), int(nums)
    paper = getObject(Paper, id=par)
    if nums == 1:
        # 可以看到隐私
        if paper:
            # 又是一个bug date写成data了
            left = Paper.objects.filter(Q(data__lt=paper.data)&Q(status=1)).order_by('data')
            right = Paper.objects.filter(Q(data__gt=paper.data)&Q(status=1)).order_by('-data')
    elif nums == 0:
        if paper:
            left = Paper.objects.filter(Q(data__lt=paper.data)&Q(status=1)&Q(secrete=0)).order_by('data')
            right = Paper.objects.filter(Q(data__gt=paper.data)&Q(status=1)&Q(secrete=0)).order_by('-data')
    if left:
        left_paper = u"""<a href="/blog/paper_detail/?pid=%s" class="label label-badge label-success"><i class="fa fa-chevron-left"></i>%s</a>""" % (left[0].id, left[0].title)
    else:
        left_paper = """<span class="label label-badge label-danger">><i class="fa fa-exclamation"></i>到头了</span>"""
    if right:
        right_paper = u"""<a href="/blog/paper_detail/?pid=%s" class="label label-badge label-success">>%s<i class="fa fa-chevron-right"></i></a>""" % (right[0].id, right[0].title)
    else:
        right_paper = """<span class="label label-badge label-danger">><i class="fa fa-exclamation"></i>到底了</span>"""
    return """<span class="pull-left label label-badge label-success">>%s</span><span class="pull-right label label-badge label-success">>%s</span>""" % (left_paper, right_paper)


@register.filter
def reply(pid):
    reply_comment = Comment.objects.filter(pcid=pid)
    if not reply_comment:
        reply_comment = [0]
    return reply_comment

@register.filter
def is_reply(pid):
    reply_comment = Comment.objects.filter(pcid=pid)
    if not reply_comment:
        return 0
    return 1

@register.filter
def user_info(uid,par):
    user = getObject(Users, id=uid)
    if user:
        if par == 'profile':
            return user.profile
        elif par == 'username':
            return user.username
        elif par == 'admin':
            return user.is_admin
        else:
            return 'error request'
    return 'None'


@register.filter
def reply_user(cid,ruid):
    comment = getObject(Comment, id=cid)
    if comment.ruid == ruid:
        return 0
    return 1


@register.filter
def web_map(par):
    category = Category.objects.filter(status=1)
    return category


@register.filter
def blogroll(par):
    r = Blogroll.objects.filter(status=1)
    return r


@register.filter
def get_weblogo(par):
    if not par:
        config = Config.objects.all()
        if config:
            config = config[0]
            return config.web_logo
    return par


@register.filter
def paper(pid, par):
    p = getObject(Paper, id=pid)
    if p:
        values = {
            'title' : p.title,
            'content' : p.content,
            'category' : p.category,
            'tag' : p.tag,
        }
        return values.get(par, '')
    return ''