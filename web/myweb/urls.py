from django.contrib import admin
from django.conf.urls import patterns, include, url

urlpatterns = patterns('myweb.views',
	url(r'^$', 'index', name='index'),
    url(r'^blog/login/$', 'login', name='login'),
    url(r'^blog/logout/$', 'logout', name='logout'),
    url(r'^blog/paper_detail/$', 'paper_detail', name='paper_detail'),
    url(r'^blog/category_detail/$', 'category_detail', name='category_detail')
    url(r'^blog/blog_paper_list/$', 'blog_paper_list', name='blog_paper_list')
    url(r'^admin/', include('admin.urls')),
)