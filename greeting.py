import site
site.addsitedir('/home/sanand/lib/python2.4/site-packages')
site.addsitedir('/usr/local/lib/python2.4/site-packages')   # for mysql-python

import os.path, cgi, ConfigParser
import web, jinja2
import smsgateway, login
from model_mysql import db, store

greetingform = web.form.Form(   # id, user, time,
    web.form.Textbox('mobile'),
    web.form.Textbox('name'),
    web.form.Dropdown('event', ['Birthday', 'Anniversary']),
    web.form.Textbox('date'),
    web.form.Dropdown('relation', ['Family', 'Friend']),
    web.form.Textarea('message'),
)

urls = (
  '/',                  'index',
  '/login/google',      'login.Google',
  '/login/twitter',     'login.Twitter',
  '/login/facebook/?',  'login.Facebook',
  '/login/mobile',      'login.Mobile',
  '/login/register',    'login.MobileRegister',
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
        return web.config._render('index.html', {
            'home'      :web.ctx.home,
            'form'      :greetingform(),
            'greetings' :web.config._session.has_key('user') and db.select('greeting', where='user = "%s"' % web.config._session.user) or None,
            'session'   :web.config._session
        })

class sms:
    def GET(self):
        web.header('Content-type', 'text/html')
        return web.config._render('sms.html', {})

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
web.config._session = web.session.Session(app, store, initializer={})
web.config._template = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(os.path.split(__file__)[0], 'template')))
web.config._render = lambda template, params: web.config._template.get_template(template).render(**params).encode('utf-8')

params = ConfigParser.RawConfigParser()
params.read(os.path.join(os.path.split(__file__)[0], 'config.ini'))
for section in params.sections(): web.config[section] = web.utils.Storage(params.items(section))

application = app.wsgifunc()
