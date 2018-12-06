from django.conf.urls import patterns, include, url


urlpatterns = patterns('admin.views',
    url(r'^$', 'admin_index', name='admin_index'),
    url(r'^admin_login$', 'admin_login', name='admin_login'),
    url(r'^admin_logout$', 'admin_logout', name='admin_logout'),

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
    url(r'^paper_push$', 'paper_push', name='paper_push'),
    url(r'^admin_markdown_upload_image$', 'admin_markdown_upload_image', name='admin_markdown_upload_image'),

    # user management
    url(r'^user_list$', 'user_list', name='user_list'),
    url(r'^user_add$', 'user_add', name='user_add'),
    url(r'^user_edit_inline$', 'user_edit_inline', name='user_edit_inline'),
    url(r'^user_edit$', 'user_edit', name='user_edit'),
    url(r'^user_del$', 'user_del', name='user_del'),


    # message management 
    url(r'^paper_comment_list$', 'paper_comment_list', name='paper_comment_list'),
    url(r'^comment_edit$', 'comment_edit', name='comment_edit'),
    url(r'^comment_edit_inline$', 'comment_edit_inline', name='comment_edit_inline'),
    url(r'^comment_del$', 'comment_del', name='comment_del'),

    url(r'^blog_message_list$', 'blog_message_list', name='blog_message_list'),


    # web config
    url(r'^web_config$', 'web_config', name='web_config'),
    url(r'^web_file$', 'web_file', name='web_file'),
    url(r'^file_edit_inline$', 'file_edit_inline', name='file_edit_inline'),
    url(r'^web_file_del$', 'web_file_del', name='web_file_del'),


    # email settings
    url(r'^email_setting$', 'email_setting', name='email_setting'),
    url(r'^email_add$', 'email_add', name='email_add'),
    url(r'^email_edit$', 'email_edit', name='email_edit'),
    url(r'^email_edit_inline$', 'email_edit_inline', name='email_edit_inline'),
    url(r'^email_del$', 'email_del', name='email_del'),
    url(r'^email_test$', 'email_test', name='email_test'),


    # tool
    url(r'^login_log_list$', 'login_log_list', name='login_log_list'),
    url(r'^login_del$', 'login_del', name='login_del'),

    url(r'^view_log_list$', 'view_log_list', name='view_log_list'),
    url(r'^view_log_del$', 'view_log_del', name='view_log_del'),

    url(r'^blogroll_list$', 'blogroll_list', name='blogroll_list'),
    url(r'^blogroll_add$', 'blogroll_add', name='blogroll_add'),
    url(r'^blogroll_edit$', 'blogroll_edit', name='blogroll_edit'),
    url(r'^blogroll_edit_inline$', 'blogroll_edit_inline', name='blogroll_edit_inline'),
    url(r'^blogroll_del$', 'blogroll_del', name='blogroll_del'),


    # databases
    url(r'^database_list$', 'database_list', name='database_list'),
    url(r'^database_backup$', 'database_backup', name='database_backup'),
    url(r'^database_recover$', 'database_recover', name='database_recover'),


    # other tool
    url(r'^admin_upload_image$', 'admin_upload_image', name='admin_upload_image'),


    # test for editormd
    url(r'^test$', 'test', name='test'),


)
