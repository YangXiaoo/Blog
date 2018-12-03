#!/usr/bin/python
# coding: utf-8
# 2018-11-27

from django import template
from django.utils.safestring import mark_safe
register = template.Library()
from admin.models import *
from myweb.models import *
from myweb.api import getObject

@register.filter
def get_config(par):
    config = Config.objects.all()
    if config:
        config = config[0]
        values = {  'title' : config.title,\
                    'keywords': config.keywords,\
                    'description' : config.description,\
                    'copyright' : config.copyright,\
                    'web_logo' : config.web_logo,\
                    'record' : config.record,\
                    'address' : config.address,\
                    'web_owner' : config.web_owner,\
                    'default_img' : config.default_img}
        return values.get(par, '')
    return ''


@register.filter
def category(par,nums):
    cate = Category.objects.order_by(str(par))[: int(nums)]
    return cate


@register.filter
def hot_paper(par,nums):
    p = Paper.objects.order_by(str(par))[: int(nums)]
    return p


@register.filter
def paper_list(par,nums=None):
    p = Paper.objects.filter(cid=int(par))
    return p


@register.filter
def preview(par,nums=None):
    return 'None'


@register.filter
def reply(pid):
    reply_comment = Comment.objects.filter(pcid=pid)
    if not reply_comment:
        reply_comment = [0]
    return reply_comment


@register.filter
def user_info(uid,par):
    user = getObject(Users, id=uid)
    if par == 'profile':
        return user.profile
    elif par == 'username':
        return user.username
    else:
        return 'error request'


@register.filter
def reply_user(cid,ruid):
    comment = getObject(Comment, id=cid)
    if comment.ruid == ruid:
        return 0
    return 1


@register.filter
def web_map():
    category = Category.objects.filter(status=1)
    return category


@register.filter
def blogroll():
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
    values = {
        'title' : p.title,
        'content' : p.content,
        'category' : p.category,
        'tag' : p.tag,
    }
    return values.get(par, '')