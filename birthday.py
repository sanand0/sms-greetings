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
  '/',              'index',
  '/login/(.+)',    'login',
  '/auth/google',   'GoogleLogin',
  '/auth/twitter',  'TwitterLogin',
  '/auth/facebook/?', 'FacebookLogin',
  '/sms',           'sms',
  '/reminder',      'reminder'
)

app = web.application(urls, globals(), autoreload=False)
session = web.session.Session(app, store, initializer={})

class index:
    def GET(self):
        web.header('Content-type', 'text/html')
        return env.get_template('index.html').render(
            form=greetingform(),
            greetings=session.has_key('user') and db.select('greeting', where='user = %d' % session.user) or None,
            session=session
        ).encode('utf-8')

class sms:
    def GET(self):
        web.header('Content-type', 'text/html')
        return env.get_template('sms.html').render().encode('utf-8')

    def POST(self):
        i = web.input('to', 'message', 'sender')
        return '''Message status: %s\nThe SMS should be sent in a few seconds.''' % smsgateway.send(i.to, i.message, i.sender)

class reminder:
    def POST(self):
        f = greetingform()
        if session.has_key('user') and f.validates():
            fields = dict(f.d)
            fields['user'] = session.user
            db.insert('greeting', **fields)
            raise web.seeother('/')
        else:
            return 'You need to log in'

class login:
    '''
    /login/{method=google|facebook|openid}          --> redirects to appropriate page, let them log in, and then come back to
    /login/{method=google|facebook|openid}/return   --> saves into session, redirects to appropriate page
    '''
    def GET(self, method):
        if method == 'google':
            # http://code.google.com/apis/accounts/docs/OpenID.html
            endpoint_dom = xml.dom.minidom.parse(urlopen('https://www.google.com/accounts/o8/id'))
            endpoint = endpoint_dom.getElementsByTagName('URI')[0].firstChild.wholeText

            raise web.seeother(endpoint + '?' + urlencode({
                'openid.return_to'          : 'http://localhost:8080/login/google.return'           ,    # TODO: Detect this? Configure this?
                'openid.mode'               : 'checkid_setup'                                       ,
                'openid.ns'                 : 'http://specs.openid.net/auth/2.0'                    ,
                'openid.claimed_id'         : 'http://specs.openid.net/auth/2.0/identifier_select'  ,
                'openid.identity'           : 'http://specs.openid.net/auth/2.0/identifier_select'  ,
                'openid.ns.ax'              : 'http://openid.net/srv/ax/1.0'                        ,
                'openid.ax.mode'            : 'fetch_request'                                       ,
                'openid.ax.required'        : 'country,email,firstname,lastname'                    ,
                'openid.ax.type.country'    : 'http://axschema.org/contact/country/home'            ,
                'openid.ax.type.email'      : 'http://schema.openid.net/contact/email'              ,
                'openid.ax.type.firstname'  : 'http://axschema.org/namePerson/first'                ,
                'openid.ax.type.lastname'   : 'http://axschema.org/namePerson/last'                 ,
            }))

        elif method == 'google.return':
            # TODO: Validate the request
            attr    = web.input()
            id      = attr['openid.identity']
            where   = web.db.sqlwhere({'id':id})
            result  = db.select('login', where=where)
            if result:
                db.update('login', where=where, attr=json.dumps(attr))
                user = result[0].user
            else:
                user = db.insert('user', mobile=None)
                db.insert('login', id=id, user=user, attr=json.dumps(attr))
            session.user = user
            session.name = attr.get('openid.ext1.value.firstname', '') + ' ' + attr.get('openid.ext1.value.lastname', '')
            if session.name == ' ': session.name = attr.get('openid.ext1.value.email', '')

            raise web.seeother('/')

        else:
            return 'Not supported'

class logout:
    def GET(self):
        del session['user']
        web.seeother('/')

application = app.wsgifunc()
