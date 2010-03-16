import site
site.addsitedir('/home/sanand/lib/python2.4/site-packages')
site.addsitedir('/usr/local/lib/python2.4/site-packages')   # for mysql-python

import web, jinja2, os.path, cgi, xml.dom.minidom, smsgateway
from model_mysql import *
from auth import GoogleLogin, TwitterLogin, FacebookLogin
from web import form
from urllib import urlopen, urlencode
try: import simplejson as json
except ImportError: from django.utils import simplejson as json

greetingform = form.Form(   # id, user, time,
    form.Textbox('mobile'),
    form.Textbox('name'),
    form.Dropdown('event', ['Birthday', 'Anniversary']),
    form.Textbox('date'),
    form.Dropdown('relation', ['Family', 'Friend']),
    form.Textarea('message'),
)

env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(os.path.split(__file__)[0], 'template')))

urls = (
  '/',                  'index',
  '/login/google',      'GoogleLogin',
  '/login/twitter',     'TwitterLogin',
  '/login/facebook/?',  'FacebookLogin',
  '/sms',               'sms',
  '/reminder',          'reminder'
)

# Facebook {'username': u'root.node', 'first_name': u'Anand', 'last_name': u'Subramanian', 'name': u'Anand Subramanian', 'locale': u'en_US', 'session_expires': 1268740800, 'pic_square': u'http://profile.ak.fbcdn.net/v225/1772/65/q655833454_7617.jpg', 'session_key': u'3.1eXoKggHvlfOw4KzSanrNg__.3600.1268740800-655833454', 'profile_url': u'http://www.facebook.com/root.node', 'uid': 655833454}
# Google {'locale': u'en', 'first_name': u'Anand', 'last_name': u'S', 'name': u'Anand S', 'email': u'root.node@gmail.com'}

class greetingapp(web.application):
    '''Patch web.application to remove .wsgi or .fcgi script name'''
    def load(self, env):
        web.application.load(self, env)
        if web.ctx.homepath.endswith('.wsgi') or web.ctx.homepath.endswith('.fcgi'):
            web.ctx.homepath = os.path.split(web.ctx.homepath)[0]
            web.ctx.home = web.ctx.homedomain + web.ctx.homepath

app = greetingapp(urls, globals(), autoreload=False)
session = web.session.Session(app, store, initializer={})

class index:
    def GET(self):
        web.header('Content-type', 'text/html')
        return env.get_template('index.html').render(
            home=web.ctx.home,
            debug='Home: ' + repr(web.ctx.home),
            form=greetingform(),
            greetings=session.has_key('user') and db.select('greeting', where='user = %d' % session.user) or None,
            session=session
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
        if 1 or session.has_key('user') and f.validates():
            # fields = dict(f.d)
            # fields['user'] = session.user
            # db.insert('greeting', **fields)
            raise web.seeother('/')
        else:
            return 'You need to log in'

class logout:
    def GET(self):
        del session['user']
        web.seeother('/')

application = app.wsgifunc()
