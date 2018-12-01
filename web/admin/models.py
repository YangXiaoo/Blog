#!/usr/bin/python
# coding: utf-8
# 2018-11-26

from django.db import models
from django.contrib.auth.models import AbstractUser
import time
import datetime


class Config(models.Model):
    title = models.CharField(max_length = 100)
    keywords = models.CharField(max_length = 100, null=True)
    description = models.CharField(max_length = 500, null=True)
    copyright = models.CharField(max_length = 200, null=True)
    web_logo = models.CharField(max_length = 100, null=True)
    record = models.CharField(max_length = 100, null=True) # 备案
    address = models.CharField(max_length = 100, null=True)
    web_owner = models.CharField(max_length = 100, null=True)
    default_img = models.CharField(max_length = 100, null=True)


class UpFiles(models.Model):
    typeid = sorts = models.IntegerField(default = 0, null=True) # 文件类型,blog=0, litpic=1
    file_name = models.CharField(max_length=100, blank=False, null=False)
    date_add = models.DateTimeField(auto_now=True, null=True)
    file_path = models.CharField(max_length=200)
    dirs = models.CharField(max_length=500)
    size = models.CharField(max_length=30, blank=True, null=True)

    def __unicode__(self):
        return self.file_name


class Blogroll(models.Model):
    """
    友情链接
    # 2018-11-30
    """
    web_name = models.CharField(max_length=200)
    web_link = models.CharField(max_length=200)
    status = models.IntegerField(default = 1, null=True)
    sorts = models.IntegerField(default = 0, null=True)



class Loginlog(models.Model):
    """
    登录日志
    """
    uid = models.IntegerField(default = 0, null=True)
    name = models.CharField(max_length=50, null=True)
    ip = models.CharField(max_length=20)
    date = models.DateField(auto_now=True)
    area = models.CharField(max_length=50)


class Viewlog(models.Model):
    """
    浏览日志
    """
    uid = models.IntegerField(default = 0, null=True)
    ip = models.CharField(max_length=20)
    date = models.DateField(auto_now=True, null=True)
    area = models.CharField(max_length=50)
    pid = models.CharField(max_length=100)



class Databases(models.Model):
    """
    数据库备份
    """
    file_name = models.CharField(max_length=100, blank=False, null=False)
    date = models.DateTimeField(auto_now=True, null=True)
    file_path = models.CharField(max_length=100)
    size = models.CharField(max_length=30, blank=True, null=True)


# 太费资源
class Thumbs(models.Model):
    """
    点赞数
    """
    uid = models.IntegerField(default = -1, null=True)
    ip = models.CharField(max_length=20)
    pid = models.IntegerField()
    is_dislike = models.IntegerField(default = 0, null=True)
    date = models.DateField(auto_now=True, null=True)