#!/usr/bin/env python

import fcgi, birthday

fcgi.WSGIServer(birthday.application).run()
