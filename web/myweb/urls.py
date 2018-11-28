from django.conf.urls import patterns, include, url


urlpatterns = patterns('myweb.views',
    url(r'^$', 'blog_index', name='blog_index'),
    url(r'^blog/login/$', 'login', name='login'),
    url(r'^blog/logout/$', 'logout', name='logout'),
    url(r'^blog/paper_detail/$', 'paper_detail', name='paper_detail'),
    url(r'^blog/category_detail/$', 'category_detail', name='category_detail'),
    url(r'^blog/blog_category_list/$', 'blog_category_list', name='blog_category_list'),
    url(r'^blog/blog_search/$', 'blog_search', name='blog_search'),
    url(r'^admin/', include('admin.urls')),

)