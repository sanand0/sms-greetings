import web
from urllib import urlopen, urlencode
from xml.dom.minidom import parse

try: import simplejson as json
except ImportError:
    from django.utils import simplejson as json

class login:
    def GET(self, method):
        if method == 'google':
            # http://code.google.com/apis/accounts/docs/OpenID.html
            endpoint_dom = parse(urlopen('https://www.google.com/accounts/o8/id'))
            endpoint = endpoint_dom.getElementsByTagName('URI')[0].firstChild.wholeText

            raise web.seeother(endpoint + '?' + urlencode({
                'openid.return_to'          : 'http://localhost:8080/login/google/return'           ,    # TODO: Detect this? Configure this?
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

        elif method == 'google/return':
            return repr(web.ctx.query)

        else:
            return 'Not supported'


'''
C. OAuth
    1. Get Google Contacts openid.ext2.request_token
'''

