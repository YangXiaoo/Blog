#!/usr/bin/python
# coding: utf-8
# 2018-11-26
from django.db import models
from django.contrib.auth.models import AbstractUser
import time
import datetime
import uuid

class User(AbstractUser):
    name = models.CharField(max_length = 100)
    uuid = models.CharField(max_length = 100)

    def __unicode__(self):
        return self.username

class Users(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length = 100)
    password = models.CharField(max_length = 100)
    name = models.CharField(max_length = 100, null=True)
    email = models.CharField(max_length = 100, null=True)
    uuid = models.CharField(max_length = 100)
    is_admin = models.BooleanField(default=False, verbose_name=u"是否管理员")
    is_active = models.BooleanField(default=True, verbose_name=u"是否激活")
    data = models.DateField(auto_now=False, auto_now_add=True)

    def __unicode__(self):
        return self.username


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length = 100)
    description = models.CharField(max_length = 100)
    paper_total = models.IntegerField(default = 0)
    data = models.DateField(auto_now=False, auto_now_add=True)
    status = models.IntegerField(default = 1, null=True)
    sorts = models.IntegerField(default = 0)
    secrete  = models.IntegerField(default = 0, null=True)


class Paper(models.Model):
    id = models.AutoField(primary_key=True)
    cid = models.IntegerField(null=False)
    category = models.CharField(max_length = 100)
    title = models.CharField(max_length = 100)
    tag = models.CharField(max_length = 100, null=True)
    keywords = models.CharField(max_length = 100, null=True)
    description = models.CharField(max_length = 500, null=True)

    data = models.DateField(auto_now=False, auto_now_add=True)
    edit_data = models.DateField(auto_now=True)

    author = models.CharField(max_length = 50, null=True)
    source = models.CharField(max_length = 50, null=True)
    views = models.IntegerField(default = 0, null=True)
    like = models.IntegerField(default = 0, null=True)
    dislike = models.IntegerField(default = 0, null=True)

    comment_total = models.IntegerField(default = 0, null=True)
    content = models.TextField(null=True)
    is_jump = models.IntegerField(default = 0, null=True)
    jumplink = models.CharField(max_length = 200, null=True)
    litpic = models.CharField(max_length = 200, null=True)
    top = models.IntegerField(default = 0, null=True)
    status = models.IntegerField(default = 1, null=True)


class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    pid = models.IntegerField(null=False)
    uid = models.IntegerField(default=0, null=True)
    ruid = models.IntegerField(default=0, null=True)
    pcid = models.IntegerField(default = -1, null=True) # 默认无父元素
    content = models.CharField(max_length = 1000, null=False)
    data = models.DateField(auto_now=False, auto_now_add=True)
    status = models.IntegerField(default = 1, null=True)
    like = models.IntegerField(default = 0)
    dislike = models.IntegerField(default = 0)


from django_markdown.models import MarkdownField
class Test(models.Model):
    content = MarkdownField()
