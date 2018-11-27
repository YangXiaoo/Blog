#!/usr/bin/python
# coding: utf-8
# 2018-11-26

from django.db import models
from django.contrib.auth.models import AbstractUser
import time
import datetime
import uuid


class Config(models.Model):
	title = models.CharField(max_length = 100)
    keywords = models.CharField(max_length = 100, null=True)
    description = models.CharField(max_length = 500, null=True)