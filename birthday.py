import site
site.addsitedir('/home/sanand/lib/python2.4/site-packages')
site.addsitedir('/usr/local/lib/python2.4/site-packages')   # for mysql-python

import web, jinja2, os.path, cgi, xml.dom.minidom, smsgateway
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

db = web.database(dbn='mysql', db='sanand_greeting', user='sanand_gr', pw='sanand')
store = web.session.DBStore(db, 'sessions')
env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(os.path.split(__file__)[0], 'template')))

urls = (
  '/',              'index',
  '/login/(.+)',    'login',
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

'''
login = (*id, +user, attr)
user = (*id, mobile, ...)
greeting = (*id,

CREATE DATABASE  `sanand_greeting` ;

Grant privileges to sanand_gr/sanand to this database

CREATE TABLE  `sanand_greeting`.`greeting` (
`id` INT NOT NULL AUTO_INCREMENT ,
`user` INT NOT NULL ,
`time` TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ,
`mobile` VARCHAR( 250 ) NOT NULL ,
`name` VARCHAR( 250 ) NOT NULL ,
`event` VARCHAR( 250 ) NOT NULL ,
`date` DATE NOT NULL ,
`relation` VARCHAR( 250 ) NOT NULL ,
`message` TEXT NOT NULL ,
PRIMARY KEY (  `id` ) ,
INDEX (  `user` )
) ENGINE = MYISAM CHARACTER SET utf8 COLLATE utf8_general_ci ;

CREATE TABLE `sanand_greeting`.`sessions` (
`session_id` CHAR(128) UNIQUE NOT NULL,
`atime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
`data` TEXT
) ENGINE MYISAM CHARACTER SET utf8 COLLATE utf8_general_ci ;

CREATE TABLE  `sanand_greeting`.`login` (
`id` VARCHAR( 250 ) NOT NULL ,
`user` INT NOT NULL ,
`attr` TEXT NOT NULL ,
PRIMARY KEY (  `id` ) ,
INDEX (  `user` )
) ENGINE = MYISAM CHARACTER SET utf8 COLLATE utf8_general_ci ;

CREATE TABLE  `sanand_greeting`.`user` (
`user` INT NOT NULL AUTO_INCREMENT ,
`mobile` VARCHAR(250),
PRIMARY KEY (  `user` )
) ENGINE = MYISAM CHARACTER SET utf8 COLLATE utf8_general_ci ;


'''

'''
openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0
openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0

openid.mode=id_res
openid.mode=id_res

openid.op_endpoint=https%3A%2F%2Fwww.google.com%2Faccounts%2Fo8%2Fud
openid.op_endpoint=https%3A%2F%2Fwww.google.com%2Faccounts%2Fo8%2Fud

openid.response_nonce=2010-02-20T13%3A37%3A23ZW_BIK9Rp4vGzNw
openid.response_nonce=2010-02-20T13%3A39%3A51Zd-fmjmaxkXX71Q

openid.return_to=http%3A%2F%2Flocalhost%3A8080%2Flogin%2Fgoogle%2Freturn
openid.return_to=http%3A%2F%2Flocalhost%3A8080%2Flogin%2Fgoogle%2Freturn

openid.assoc_handle=AOQobUdfSj-o130r9GPozaqCxV7G_ifUMEYn3zkTe63y_vWiQDOH8zGS
openid.assoc_handle=AOQobUerEO7XZwm6lIUxRZ0zcGSF_IkEZIJl6Kyj90lqX7uIXOhMj6gj

openid.signed=op_endpoint%2Cclaimed_id%2Cidentity%2Creturn_to%2Cresponse_nonce%2Cassoc_handle
openid.signed=op_endpoint%2Cclaimed_id%2Cidentity%2Creturn_to%2Cresponse_nonce%2Cassoc_handle
openid.signed=op_endpoint%2Cclaimed_id%2Cidentity%2Creturn_to%2Cresponse_nonce%2Cassoc_handle%2Cns.ext1%2Cext1.mode%2Cext1.type.firstname%2Cext1.value.firstname%2Cext1.type.email%2Cext1.value.email%2Cext1.type.lastname%2Cext1.value.lastname%2Cext1.type.country%2Cext1.value.country

openid.sig=Wu48tQYpdQRhxpb1zWwCUYcsdxY%3D
openid.sig=LL1OU1qT5KSBUGqTzxs23LmPPVo%3D

openid.identity=https%3A%2F%2Fwww.google.com%2Faccounts%2Fo8%2Fid%3Fid%3DAItOawkdOL1Hza1_GjtoGzoFL8nVjSmNONRW8fQ
openid.identity=https%3A%2F%2Fwww.google.com%2Faccounts%2Fo8%2Fid%3Fid%3DAItOawkdOL1Hza1_GjtoGzoFL8nVjSmNONRW8fQ

openid.claimed_id=https%3A%2F%2Fwww.google.com%2Faccounts%2Fo8%2Fid%3Fid%3DAItOawkdOL1Hza1_GjtoGzoFL8nVjSmNONRW8fQ
openid.claimed_id=https%3A%2F%2Fwww.google.com%2Faccounts%2Fo8%2Fid%3Fid%3DAItOawkdOL1Hza1_GjtoGzoFL8nVjSmNONRW8fQ

openid.ns.ext1=http%3A%2F%2Fopenid.net%2Fsrv%2Fax%2F1.0
openid.ext1.mode=fetch_response
openid.ext1.type.firstname=http%3A%2F%2Faxschema.org%2FnamePerson%2Ffirst
openid.ext1.value.firstname=Anand
openid.ext1.type.email=http%3A%2F%2Fschema.openid.net%2Fcontact%2Femail
openid.ext1.value.email=root.node%40gmail.com
openid.ext1.type.lastname=http%3A%2F%2Faxschema.org%2FnamePerson%2Flast
openid.ext1.value.lastname=S
openid.ext1.type.country=http%3A%2F%2Faxschema.org%2Fcontact%2Fcountry%2Fhome
openid.ext1.value.country=GB

'''
