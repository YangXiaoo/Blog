from django.conf.urls import patterns, include, url


urlpatterns = patterns('myweb.views',
    url(r'^$', 'blog_index', name='blog_index'),

    url(r'^qqconnect$', 'qq_connect', name='qq_connect'),
    url(r'^qq_login$', 'qq_login', name='qq_login'),
    url(r'^bind_account_qq$', 'bind_account_qq', name='bind_account_qq'),

    url(r'^blog/login/$', 'login', name='login'),
    url(r'^blog/sign/$', 'sign', name='sign'),
    url(r'^blog/logout/$', 'logout', name='logout'),

    url(r'^blog/paper_detail/$', 'paper_detail', name='paper_detail'),
    url(r'^blog/category_detail/$', 'category_detail', name='category_detail'),
    url(r'^blog/blog_category_list/$', 'blog_category_list', name='blog_category_list'),
    url(r'^blog/blog_search/$', 'blog_search', name='blog_search'),
    url(r'^blog/thumbs/$', 'blog_thumbs', name='blog_thumbs'),
    url(r'^blog/paper_comment/$', 'paper_comment', name='paper_comment'),

    url(r'^admin/', include('admin.urls')),
    url(r'.*', 'request_error', name='request_error'),

)