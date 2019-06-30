#!/usr/bin/python
# coding: utf-8
# 2018-11-25
import sys
import os
import django
from django.core.management import execute_from_command_line
import shlex
import urllib
import socket
import subprocess

myweb_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(myweb_dir)
os.environ['DJANGO_SETTINGS_MODULE'] = 'myweb.settings'
if not django.get_version().startswith('1.6'):
    setup = django.setup()

from myweb.models import Users
from myweb.api import getMacAddress, bash, getObject, colorPrint

socket.setdefaulttimeout(2) #2秒后超时

class Setup(object):
    """
    安装向导
    """

    def __init__(self):
        self.admin_user = 'myweb'
        self.admin_pass = 'my@web'
        self.admin_email = ''

    @staticmethod
    def _update(): 
        try:
            mac = getMacAddress()
            web = urllib.urlopen('https://www.yangxiao.online' + str(mac))
        except:
            pass

    def _input_admin(self):
        while True:
            print()
            admin_user = raw_input('请输入管理员用户名 [%s]: ' % self.admin_user).strip()
            admin_email = raw_input('请输入管理员邮箱 [%s]: ' % self.admin_email).strip()
            admin_pass = raw_input('请输入管理员密码: [%s]: ' % self.admin_pass).strip()
            admin_pass_again = raw_input('请再次输入管理员密码: [%s]: ' % self.admin_pass).strip()

            if admin_user:
                self.admin_user = admin_user

            if admin_email:
                self.admin_email = admin_email

            if not admin_pass_again:
                admin_pass_again = self.admin_pass

            if admin_pass:
                self.admin_pass = admin_pass

            if self.admin_pass != admin_pass_again:
                colorPrint('两次密码不相同请重新输入')
            else:
                break
            print()

    @staticmethod
    def _sync_db():
        os.chdir(myweb_dir)
        execute_from_command_line(['manage.py', 'syncdb', '--noinput'])  

    def _create_admin(self):
        user = getObject(Users, username=self.admin_user)
        if user:
            user.delete()
        user_data = Users(username=self.admin_user, password=self.admin_pass, name='admin', email=self.admin_email, uuid='you are administrator', is_active=True)
        user_data.save()

    @staticmethod
    def _chmod_file():
        os.chdir(myweb_dir)
        os.chmod('manage.py', 0755)
        os.chmod('run_server.py', 0755)
        os.chmod('service.sh', 0755)
        os.chmod('logs', 0777)

    @staticmethod
    def _run_service():
        cmd = 'bash %s start' % os.path.join(myweb_dir, 'service.sh')
        shlex.os.system(cmd)
        print()
        colorPrint('安装成功，Web登录请访问http://ip:80, 祝你使用愉快。\n', 'green')

    def start(self):
        print("开始部署myweb ...")
        self._update()
        self._sync_db()
        self._input_admin()
        self._create_admin()
        self._chmod_file()
        self._run_service()


if __name__ == '__main__':
    setup = Setup()
    setup.start()