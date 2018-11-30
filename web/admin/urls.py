from django.conf.urls import patterns, include, url


urlpatterns = patterns('admin.views',
    url(r'^$', 'admin_index', name='admin_index'),

    # paper category management
    url(r'^category_add$', 'category_add', name='category_add'),
    url(r'^category_edit$', 'category_edit', name='category_edit'),
    url(r'^category_list$', 'category_list', name='category_list'),
    url(r'^category_del$', 'category_del', name='category_del'),
    url(r'^category_edit_inline$', 'category_edit_inline', name='category_edit_inline'),

    # paper managemant
    url(r'^paper_list$', 'paper_list', name='paper_list'),
    url(r'^paper_add$', 'paper_add', name='paper_add'),
    url(r'^paper_edit$', 'paper_edit', name='paper_edit'),
    url(r'^paper_edit_inline$', 'paper_edit_inline', name='paper_edit_inline'),
    url(r'^paper_del$', 'paper_del', name='paper_del'),
    url(r'^admin_markdown_upload_image$', 'admin_markdown_upload_image', name='admin_markdown_upload_image'),

    # user management
    url(r'^user_list$', 'user_list', name='user_list'),

    # message management
    url(r'^paper_comment_list$', 'paper_comment_list', name='paper_comment_list'),
    url(r'^blog_message_list$', 'blog_message_list', name='blog_message_list'),

    # webconfig
    url(r'^web_config$', 'web_config', name='web_config'),

    # tool
    url(r'^login_log_list$', 'login_log_list', name='login_log_list'),
    url(r'^view_log_list$', 'view_log_list', name='view_log_list'),
    url(r'^blogroll_list$', 'blogroll_list', name='blogroll_list'),

    # databases
    url(r'^database_list$', 'database_list', name='database_list'),
    url(r'^database_back_list$', 'database_back_list', name='database_back_list'),


    # test for editormd
    url(r'^test$', 'test', name='test'),


)
