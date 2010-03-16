import site
site.addsitedir('/home/sanand/lib/python2.4/site-packages')
site.addsitedir('/usr/local/lib/python2.4/site-packages')   # for mysql-python

import web, jinja2, os.path, cgi, xml.dom.minidom, smsgateway, login
from model_mysql import *
from urllib import urlopen, urlencode
try: import simplejson as json
except ImportError: from django.utils import simplejson as json

greetingform = web.form.Form(   # id, user, time,
    web.form.Textbox('mobile'),
    web.form.Textbox('name'),
    web.form.Dropdown('event', ['Birthday', 'Anniversary']),
    web.form.Textbox('date'),
    web.form.Dropdown('relation', ['Family', 'Friend']),
    web.form.Textarea('message'),
)

env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(os.path.split(__file__)[0], 'template')))

urls = (
  '/',                  'index',
  '/login/google',      'login.Google',
  '/login/twitter',     'login.Twitter',
  '/login/facebook/?',  'login.Facebook',
  '/logout',            'login.Logout',
  '/sms',               'sms',
  '/reminder',          'reminder'
)

class greetingapp(web.application):
    '''Patch web.application to remove .wsgi or .fcgi script name'''
    def load(self, env):
        web.application.load(self, env)
        if web.ctx.homepath.endswith('.wsgi') or web.ctx.homepath.endswith('.fcgi'):
            web.ctx.homepath = os.path.split(web.ctx.homepath)[0]
            web.ctx.home = web.ctx.homedomain + web.ctx.homepath

class index:
    def GET(self):
        web.header('Content-type', 'text/html')
        return env.get_template('index.html').render(
            home=web.ctx.home,
            form=greetingform(),
            greetings=web.config._session.has_key('user') and db.select('greeting', where='user = "%s"' % web.config._session.user) or None,
            session=web.config._session
        ).encode('utf-8')

class sms:
    def GET(self):
        web.header('Content-type', 'text/html')
        return env.get_template('sms.html').render().encode('utf-8')
        return env.get_template('sms.html').render().encode('utf-8')

    def POST(self):
        i = web.input('to', 'message', 'sender')
        return '''Message status: %s\nThe SMS should be sent in a few seconds.''' % smsgateway.send(i.to, i.message, i.sender)

class reminder:
    def POST(self):
        f = greetingform()
        if web.config._session.has_key('user') and f.validates():
            fields = dict(f.d)
            fields['user'] = web.config._session.user
            db.insert('greeting', **fields)
            raise web.seeother('/')
        else:
            return 'You need to log in'

app = greetingapp(urls, globals(), autoreload=True)
session = web.session.Session(app, store, initializer={})
web.config._session = session
application = app.wsgifunc()
