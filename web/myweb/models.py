#!/usr/bin/python
# coding: utf-8
# 2018-11-26
from django.db import models
import time
import datetime
import uuid

class Session(models.Model):
    

class Users(models.Model):
    username = models.CharField(max_length = 100)
    password = models.CharField(max_length = 100)
    name = models.CharField(max_length = 100, null=True)
    gender = models.IntegerField(default = 0, null=True) # 0:man, 1:women
    email = models.CharField(max_length = 100, null=True)
    profile = models.CharField(max_length = 100, null=True) 
    third_log = models.IntegerField(default = 0, null=True)
    uuid = models.CharField(max_length = 100)
    log_total = models.IntegerField(default = 0, null=True)
    is_admin = models.IntegerField(default = 0, null=True)
    is_active = models.IntegerField(default = 1, null=True)
    data = models.DateField(auto_now_add=True, null=True)
    user_info = models.CharField(max_length = 500, null=True)
    last_login =  models.DateField(auto_now=True, null=True)
    last_ip = models.CharField(max_length = 20, null=True)

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
    attribute = models.CharField(max_length = 10,null=True)
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
    pid = models.IntegerField(null=False)
    uid = models.IntegerField(default=0, null=True)
    ruid = models.IntegerField(default=0, null=True)
    pcid = models.IntegerField(default = -1, null=True) # 默认无父元素
    content = models.CharField(max_length = 1000, null=False)
    data = models.DateField(auto_now=False, auto_now_add=True)
    status = models.IntegerField(default = 1, null=True)
    like = models.IntegerField(default = 0, null=True)
    dislike = models.IntegerField(default = 0, null=True)
