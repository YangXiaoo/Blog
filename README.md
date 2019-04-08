#Blog
[首页链接](http://yangxiao.online "首页链接")
[后台首页](http://yangxiao.online/admin/ "后台首页")

采用python2.7，django1.6

一键安装部署，方法：
```shell
[root]# cd install
[root]# python install.py

```
安装中会有提示输入邮箱，部署数据库等操作。部署完成后即可使用，网络服务基于tornado。

服务启用操作：
```shell
[root]# bash service.sh start # 启动服务
[root]# bash service.sh restart # 重启服务
[root]# bash service.sh stop # 关闭服务
```
# 功能
1. 博客使用markdown
2. 首页查看用户活跃状态
3. 采集用户端数据，并生成图表
4. 邮箱推送文章，用户回复通过邮箱提醒
5. 第三方QQ登录
6. 博客设置隐私，只有管理员能够在主页查看并显示
7. 主页名称，描述，备案等信息能够后台修改
8. mysql数据备份
9. 文件上传下载功能，简洁网盘

# 展示
![](http://yangxiao.online/static/files/20190407-200856-b64e/QQ浏览器截图20190407200840.png)
![](http://yangxiao.online/static/files/20190407-201239-7c9a/QQ浏览器截图20190407200922.png)
![](http://yangxiao.online/static/files/20190407-201247-a69e/QQ浏览器截图20190407200949.png)
![](http://yangxiao.online/static/files/20190407-201255-8b86/QQ浏览器截图20190407201003.png)
![](http://yangxiao.online/static/files/20190407-201304-135f/QQ浏览器截图20190407201034.png)
![](http://yangxiao.online/static/files/20190407-201312-730f/QQ浏览器截图20190407201056.png)
![](http://yangxiao.online/static/files/20190407-201324-4ec2/QQ浏览器截图20190407201148.png)
![](http://yangxiao.online/static/files/20190407-201332-905f/QQ浏览器截图20190407201210.png)
![](http://yangxiao.online/static/files/20190407-201340-cd14/QQ浏览器截图20190407201229.png)

#升级
- 2018-12-8 基本功能完成
- 2019-4-8 博客前端使用`ZUI`框架，并修复一些BUG

#说明
- 本人QQ: 1270009836


