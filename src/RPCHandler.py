# !/usr/bin/env python


import os

from django.utils import simplejson
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util


class MainPage(webapp.RequestHandler):
    """ Renders the main template."""
    def get(self):
        template_values = { 'title':'AJAX Add (via GET)', }
        path = os.path.join(os.path.dirname(__file__), "index.html")
        self.response.out.write(template.render(path, template_values))


class RPCHandler(webapp.RequestHandler):
    """ Allows the functions defined in the RPCMethods class to be RPCed."""
    def __init__(self):
        webapp.RequestHandler.__init__(self)
        self.methods = RPCMethods()
 
    def get(self):
        func = None
        
        action = self.request.get('action')
        if action:
            if action[0] == '_':
                self.error(403) # access denied
            return
        else:
            func = getattr(self.methods, action, None)
   
        if not func:
            self.error(404) # file not found
            return
     
        args = ()
        while True:
            key = 'arg%d' % len(args)
            val = self.request.get(key)
            if val:
                args += (simplejson.loads(val),)
            else:
                break
            result = func(*args)
            self.response.out.write(simplejson.dumps(result))

    def post(self):
        args = simplejson.loads(self.request.body)
        func, args = args[0], args[1:]
        if func[0] == '_':
            self.error(403) # access denied
            return
        func = getattr(self.methods, func, None)
        if not func:
            self.error(404) # file not found
            return #@IndentOk

        result = func(*args)
        self.response.out.write(simplejson.dumps(result))


class RPCMethods:
    """ Defines the methods that can be RPCed.
    NOTE: Do not allow remote callers access to private/protected "_*" methods.
    """
    def Add(self, *args):
        # The JSON encoding may have encoded integers as strings.
        # Be sure to convert args to any mandatory type(s).
        ints = [int(arg) for arg in args]
        return sum(ints)
        
 
def main():
    app = webapp.WSGIApplication([
      ('/rpc', RPCHandler),
      ], debug=True)
    util.run_wsgi_app(app)

if __name__ == '__main__':
    main()