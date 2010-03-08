import urllib

USERNAME = 'sanand0'
PASSWORD = 'sanand'

def send(to, msg, sender=""):
    ''' TODO: Error handling '''
    params = urllib.urlencode({
        'username': USERNAME,
        'password': PASSWORD,
        'sender':   sender,
        'message':  msg,
        'to':       to
    })

    return urllib.urlopen('http://bulksms.gateway4sms.com/pushsms.php?' + params).read()
