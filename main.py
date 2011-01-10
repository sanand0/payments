#!/usr/bin/env python

'''
Keep it simple. Very simple.
'''

import tornado.web, tornado.options, tornado.httpserver, tornado.ioloop
import os.path
import logging
import urllib
import random
try:
  import json
except:
  from django.utils import simplejson as json

TOKENS = (
'Aj3nS39JS01mS3jek3',
'39JS01mS3jek3Aj3nS',
'1mS3jek3Aj3nS39JS0',
'jek3Aj3nS39JS01mS3',
)

USERS = {
 'subramanian_anand@infosys.com': 'anand',
 'phil_freegard@infosys.com': 'phil',
}

ROOT = os.path.dirname(__file__)

class Page(tornado.web.RequestHandler):
    '''Any class that requires @tornado.web.authenticated inherits from this'''
    def get_current_user(self):
        return self.get_secure_cookie("uid")

class LoginPage(Page):
    def get(self):
        handler = self
        self.render('template/login.html')

    def post(self):
        username = self.get_argument('username', None)
        password = self.get_argument('password', None)
        if USERS.get(username, None) == password:
            self.set_secure_cookie('uid', username)
        self.redirect(self.get_argument('next', '/'))

class LogoutPage(Page):
    def get(self):
        self.clear_cookie('uid')
        self.redirect(self.get_argument('next', '/'))

class TemplatePage(Page):
    def get(self, page='index'):
        self.render('template/' + page + '.html')

class ShopPage(tornado.web.RequestHandler):
    def get(self):
        data = json.loads(open(os.path.join(ROOT, 'products.json')).read())
        self.render('template/shop.html', data=data)

class ShipmentPage(tornado.web.RequestHandler):
    def get(self):
        token = self.get_argument('token', '')
        valid = token in TOKENS
        self.render('template/shipment.html', valid=valid)

class PaymentPage(Page):
    @tornado.web.authenticated
    def get(self):
        handler = self
        # Render the response
        self.render('template/payment.html', handler=handler)

    @tornado.web.authenticated
    def post(self):
        callback = self.get_argument('callback', '/')
        if self.get_argument('pay', ''):
            # TODO: deduct amount
            # If successful:
            token = random.choice(TOKENS)
            self.redirect(callback + '?' + urllib.urlencode({
                'token': token,
            }))

        self.redirect(callback)

class BalancePage(Page):
    @tornado.web.authenticated
    def get(self):
        self.write('TODO: balance page')

application = tornado.web.Application([
    # Documentation
    (r'/',          TemplatePage),

    # Shop pages
    (r'/shop',      ShopPage),
    (r'/ship',      ShipmentPage),

    # Bank pages
    (r'/balance',   BalancePage),
    (r'/login',     LoginPage),
    (r'/logout',    LogoutPage),
    (r'/pay',       PaymentPage),
],
  debug=True,
  cookie_secret='kRFo2i3jU213oiKewklfmlDkMdSfkJ4xroi3U09x',
  static_path = os.path.join(os.path.dirname(__file__), 'static'),
  login_url   = '/login',
)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8910)
    tornado.ioloop.IOLoop.instance().start()
