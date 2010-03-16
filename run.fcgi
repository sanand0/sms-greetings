#!/usr/bin/env python

import fcgi, greeting

fcgi.WSGIServer(greeting.application).run()
