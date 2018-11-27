#!/usr/bin/python
# coding: utf-8
# 2018-11-25

import os
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpserver
from tornado.options import options, define as _define
import django
try:
    remote_ip = os.environ.get('MYWEB_CLIENT').split()[0]
except (IndexError, AttributeError):
    remote_ip = os.popen("who -m | awk '{ print $NF }'").read().strip('()\n')

os.environ['DJANGO_SETTINGS_MODULE'] = 'myweb.settings'
if not django.get_version().startswith('1.6'):
    setup = django.setup()
from myweb.settings import IP, PORT

# Not need , just in case of repeat defined   
def define(name, default=None, type=None, help=None, metavar=None,
           multiple=False, group=None, callback=None):
    if name not in options._options:
        return _define(name, default, type, help, metavar,
           multiple, group, callback)
    
tornado.options.define = define
define("port", default=PORT, help="run on the given port", type=int)
define("host", default=IP, help="run port on given host", type=str)

def main():
    from django.core.wsgi import get_wsgi_application
    import tornado.wsgi
    wsgi_app = get_wsgi_application()
    container = tornado.wsgi.WSGIContainer(wsgi_app)
    setting = {
        'cookie_secret': 'DFksdfsasdfkasdfFKwlwfsdfsa1204mx',
        'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
        'static_path': os.path.join(os.path.dirname(__file__), 'static'),
        'debug': False,
    }
    tornado_app = tornado.web.Application(
        [
            (r"/static/(.*)", tornado.web.StaticFileHandler,
             dict(path=os.path.join(os.path.dirname(__file__), "static"))),
            ('.*', tornado.web.FallbackHandler, dict(fallback=container)),
        ], **setting)

    server = tornado.httpserver.HTTPServer(tornado_app)
    server.listen(options.port, address=IP)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    print("Run server on %s:%s" % (options.host, options.port))
    main()