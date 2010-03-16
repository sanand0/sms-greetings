import web
from auth import webpyauth, auth # WebappAuth, RequestRedirect, HttpException

class Logout:
    def GET(self):
        if web.config._session.has_key('user'): del web.config._session.user
        if web.config._session.has_key('name'): del web.config._session.name
        raise web.seeother('/')

class Login:
    def GET(self):
        try:
            if self.has_user():
                self.get_authenticated_user(self._on_auth)
                raise webpyauth.RequestRedirect(url=web.ctx.home)
            else:
                self.authenticate_redirect()
        except webpyauth.RequestRedirect, e:
            raise web.seeother(e.url)

    def _on_auth(self, user):
        if user:
            # Store this information and assign a user ID
            key, name, attr = self.get_user(user)
            web.config._session.user = key
            web.config._session.name = name
        else:
            web.debug('Did not get user')
            # TODO: Send to failed auth page or something.


class Google(webpyauth.WebappAuth, auth.GoogleMixin, Login):
    def __init__(self):
        webpyauth.WebappAuth.__init__(self)

    def has_user(self): return web.input().get("openid.mode", None)

    # Google user = {'locale': u'en', 'first_name': u'Anand', 'last_name': u'S', 'name': u'Anand S', 'email': u'root.node@gmail.com'}
    def get_user(self, user): return 'gg:' + user.get('email'), user.get('name', '') or user.get('email'), user

class Twitter(webpyauth.WebappAuth, auth.TwitterMixin, Login):
    def __init__(self):
        # Register apps at http://twitter.com/apps/new
        # http://twitter.com/oauth_clients/details/97296
        webpyauth.WebappAuth.__init__(self,
            twitter_consumer_key    = 'GuXOFFfhnlxs1kgMpsQhw',
            twitter_consumer_secret = 'VL28QvbgbqW8cAssCUzqrtaXK3MxNM0pmXmeuQHYFQ',
        )

    def has_user(self): return web.input().get("oauth_token", None)
    
    def get_user(self, user): return 'tw:', '', {}

class Facebook(webpyauth.WebappAuth, auth.FacebookMixin, Login):
    def __init__(self):
        # http://www.facebook.com/developers/editapp.php?app_id=369944562357
        # Set Connect URL to the return value
        webpyauth.WebappAuth.__init__(self,
            facebook_api_key    = 'b7166989bdf0ad62b809237091d5d576',
            facebook_secret     = '2b1b0705b4e1bea41f70402ea49799d7',
        )

    def has_user(self): return web.input().get("session", None)

    # Facebook user = {'username': u'root.node', 'first_name': u'Anand', 'last_name': u'Subramanian', 'name': u'Anand Subramanian', 'locale': u'en_US', 'session_expires': 1268740800, 'pic_square': u'http://profile.ak.fbcdn.net/v225/1772/65/q655833454_7617.jpg', 'session_key': u'3.1eXoKggHvlfOw4KzSanrNg__.3600.1268740800-655833454', 'profile_url': u'http://www.facebook.com/root.node', 'uid': 655833454}
    def get_user(self, user): return 'fb:' + str(user.get('uid', None)), user.get('name', ''), user
