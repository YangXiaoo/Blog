from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('admin.views',
    url(r'^$', 'index', name='index'),
    url(r'^category_add$', 'category_add', name='category_add'),
    url(r'^category_edit$', 'category_edit', name='category_edit'),
    url(r'^category_list$', 'category_list', name='category_list'),
    url(r'^paper_list$', 'paper_list', name='paper_list'),
    url(r'^paper_add$', 'paper_add', name='paper_add'),
    url(r'^paper_edit$', 'paper_edit', name='paper_edit'),
)
