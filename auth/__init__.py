import web
import webpyauth # WebappAuth, RequestRedirect, HttpException
import auth

class GoogleLogin(webpyauth.WebappAuth, auth.GoogleMixin):
    def GET(self):
        try:
            if web.input().get("openid.mode", None):
                self.get_authenticated_user(self._on_auth)
                # TODO: Store
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

