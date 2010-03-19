import urllib, web

def send(to, message, sender="SMSGreet"):
    ''' TODO: validations and error handling '''
    if to.startswith('44'): url = web.config.mobile['44']
    else:                   url = web.config.mobile['91']

    args = {'to': to, 'sender': urllib.quote_plus(sender), 'message': urllib.quote_plus(message)}
    web.debug(url % args)
    return urllib.urlopen(url % args).read()
