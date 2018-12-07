# Blog
[首页链接](http://www.lxa.kim "首页链接")
[后台首页](http://www.lxa.kim/admin/ "后台首页")

采用python2.7，django1.6

一键安装部署，方法：
```shell
[root]# cd install
[root]# python install.py

```
安装中会有提示输入邮箱，部署数据库等操作。部署完成后即可使用部署基于tornado。

服务启用操作：
```shell
[root]# bash service.sh start # 启动服务
[root]# bash service.sh restart # 重启服务
[root]# bash service.sh stop # 关闭服务
```
# 功能
1. 博客使用markdown
2. 首页查看用户活跃状态
3. 采集用户端数据
4. 邮箱推送文章，用户回复通过邮箱提醒
5. 第三方QQ登录
6. 博客设置隐私，只有管理员能够在主页查看并显示
7. 主页名称，描述，备案等信息能够后台修改
8. mysql数据备份
9. 文件上传下载功能，简洁网盘

# 升级
- 2018-12-8基本功能完成

# 说明
-  前端模板来源于[苏晓信](http://www.sxxblog.com/ "苏晓信")
- 本人qq: 1270009836


