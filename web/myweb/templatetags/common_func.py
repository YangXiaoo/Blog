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
def getConfig(par):
    config = Config.objects.all()
    if config:
        if par == 'title':
        	return config.title
        elif par == 'keywords':
        	return config.keywords
        elif par == 'description':
        	return config.description
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