import web
import webpyauth # WebappAuth, RequestRedirect, HttpException
import auth

class Login:
    def GET(self):
        try:
            if self.has_user():
                self.get_authenticated_user(self._on_auth)
                return 'Alpha ' + repr(self.user)
            else:
                self.authenticate_redirect()
        except webpyauth.RequestRedirect, e:
            raise web.seeother(e.url)

        return 'User is None'

    def _on_auth(self, user):
        if user:
            web.debug('Got user: ' + repr(user))
            self.user = user
        else:
            web.debug('Did not get user')


class GoogleLogin(webpyauth.WebappAuth, auth.GoogleMixin, Login):
    def has_user(self):
        return web.input().get("openid.mode", None)

class TwitterLogin(webpyauth.WebappAuth, auth.TwitterMixin, Login):
    def __init__(self):
        # Register apps at http://twitter.com/apps/new
        # http://twitter.com/oauth_clients/details/97296
        webpyauth.WebappAuth.__init__(self,
            twitter_consumer_key    = 'GuXOFFfhnlxs1kgMpsQhw',
            twitter_consumer_secret = 'VL28QvbgbqW8cAssCUzqrtaXK3MxNM0pmXmeuQHYFQ',
        )

    def has_user(self):
        return web.input().get("oauth_token", None)

class FacebookLogin(webpyauth.WebappAuth, auth.FacebookMixin, Login):
    def __init__(self):
        # http://www.facebook.com/developers/editapp.php?app_id=369944562357
        webpyauth.WebappAuth.__init__(self,
            facebook_api_key    = 'b7166989bdf0ad62b809237091d5d576',
            facebook_secret     = '2b1b0705b4e1bea41f70402ea49799d7',
        )

    def has_user(self):
        return web.input().get("session", None)
