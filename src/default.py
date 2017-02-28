import os
import urllib

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp import template

from model import DbFile
from model import Product
from model import Store

def admin_required(handler_method):
    """A decorator to require that a user be logged in to access a handler.
    
    To use it, decorate your get() method like this:
    
    @admin_required
    def get(self):
        user = users.get_current_user(self)
        self.response.out.write('Hello, ' + user.nickname())
    
    We will redirect to a login page if the user is not logged in. We always
    redirect to the request URI, and Google Accounts only redirects back as a GET
    request, so this should not be used for POSTs.
    """
    def check_login(self, *args):
        uri = '/'
        if self.request.method == 'GET':
            uri = self.request.uri
        if not users.is_current_user_admin():
            self.redirect(users.create_login_url(uri))
            return
        else:
            handler_method(self, *args)
    return check_login

class MainPage(webapp.RequestHandler):
    """The root page by which all Request handlers in the application should subclass"""
    def get(self):
        self.generate('base.html')
    def _getDefaultStore(self):
        query = Store.gql('where name = :name', name = 'default')
        store = query.get()
        if store == None:
            store = Store(name = 'default', merchantid = '0', useSandbox = 'true')
            store.put()
        return store
    def _create_table(self, seq, n):
        table = []
        temp = []
        i = 0
        for item in seq:
            temp.append(item)
            i += 1
            if i % n == 0:
                table.append(temp)
                temp = []
        table.append(temp)
        return table

    def generate(self, template_name, template_values={}):
        """Base classes should call this instead of generating their own template.
        This will generate all the base class template values and append the subclasses
        template values.  It then calls the template and writes the result to the browser"""
        recentBlogs = []
        
        values = {
            'request': self.request,
            'user': users.get_current_user(),
            'recentBlogs': recentBlogs,
            'login_url': users.create_login_url(self.request.uri),
            'logout_url': users.create_logout_url(self.request.uri),
            'debug': self.request.get('deb'),
            'isAdmin': users.is_current_user_admin(),
            'currentURI': self.request.uri,
            'application_name': 'bananasbrownies',
            'store' : self._getDefaultStore(), }
        values.update(template_values)
        directory = os.path.dirname(__file__)
        path = os.path.join(directory, os.path.join('templates', template_name))
        self.response.out.write(template.render(path, values, debug=True))
        
    def generatePagedFromQuery(self, query, template_name, template_values={}, numRecordsToFetch = 20, tableColumns = 3):
        """This assumes you want to deliver paged content from a given query"""
        currentPage = self.request.get("page")
        if not currentPage:
            currentPage = 0
        else:
            currentPage = int(currentPage)
        totalRecords = query.count()
        totalPages = totalRecords / numRecordsToFetch
        if currentPage > totalPages:
            currentPage = totalPages
        dbEntries = query.fetch(numRecordsToFetch, numRecordsToFetch * currentPage)
        
        firstPage = 0
        previousPage = currentPage - 1
        nextPage = currentPage + 1
        lastPage = totalPages
        
        template_values = { 'dbEntries' : dbEntries }
        template_values['entryTable'] = self._create_table(dbEntries, tableColumns)
        #if firstPage <> lastPage:
        
        if previousPage > firstPage:
            template_values['previousPage'] = str(previousPage)        
        if nextPage < lastPage:
            template_values['nextPage'] = str(nextPage)
        if firstPage <> lastPage:
            template_values['firstPage'] = str(firstPage) #needs string because zero evaluates to false
            template_values['currentPage'] = str(currentPage)
            template_values['lastPage'] = str(lastPage)
        self.generate(template_name, template_values)
        
    def postRedirect(self):
        redirectPage = '/' + self.__class__.__name__        
        lastPage = self.request.get("last")
        if lastPage:
            redirectPage += '?page=' + str(lastPage)
        self.redirect(redirectPage)

class Demo(MainPage):
    def get(self):
        self.generate('demo.html')
        
class Art(MainPage):
    def get(self):
        self.generate('art.html')     

class ProductInfo(MainPage):
    def get(self):
        query = Product.all()        
        self.generatePagedFromQuery(query, "ProductInfo.html")

class ContactUs(MainPage):
    def get(self):
        self.generate('ContactUs.html')
        
class AboutUs(MainPage):
    def get(self):
        self.generate('AboutUs.html')
        
class Administration(MainPage):
    """All administration pages should use this page as the base class.  It will check permissions"""
    @admin_required
    def get(self):
        self.generate('Administration.html')

class FileUpload(MainPage):
    @admin_required
    def get(self):
        query = DbFile.all() #db.GqlQuery("SELECT * FROM BlogEntry")
        self.generatePagedFromQuery(query, "FileUpload.html")
    @admin_required
    def post(self):
        thefile = self.request.params['file']
        myFile = DbFile(name=thefile.filename,
                        data=db.Blob(thefile.value),
                        type=thefile.type)
        myFile.put()
        self.postRedirect()

class DownloadFile(MainPage):
    def get(self):
        uri = self.request.uri
        fileName = urllib.unquote(uri[uri.rfind('/') + 1:])
        query = DbFile.gql('where name = :name', name = fileName)
        fileEntry  = query.get()
        if fileEntry == None:
            self.error(404)
            self.response.out.write("Not found")
            return
        else:
            self.response.headers['Content-Type'] = fileEntry.type
            self.response.out.write(fileEntry.data)
            
class DeleteFile(MainPage):
    @admin_required
    def get(self):        
        fileEntry = db.get(self.request.get("file_id"))
        fileEntry.delete()
        self.redirect('/FileUpload')

class CreateProduct(MainPage):
    @admin_required
    def get(self):
        query = Product.all() #db.GqlQuery("SELECT * FROM BlogEntry")        
        self.generatePagedFromQuery(query, "CreateProduct.html")
    @admin_required
    def post(self):
        thefile = self.request.params['prductImage']
        newImageFile = DbFile(name=thefile.filename,
                              data=db.Blob(thefile.value),
                              type=thefile.type)
        newImageFile.put()
        theDetailFile = self.request.params['prductDetailImage']
        newImageDetailFile = DbFile(name=theDetailFile.filename,
                                    data=db.Blob(theDetailFile.value),
                                    type=theDetailFile.type)
        newImageDetailFile.put()
        newName = self.request.params['productName']
        newDescription = self.request.params['productDescription']
        newPrice = float(self.request.params['productPrice'])
        newImagePath = '/Files/' + newImageFile.name
        newImageDetailPath = '/Files/' + newImageDetailFile.name
        
        product = Product(name=newName,
                          description=newDescription,
                          price=newPrice,
                          imagePath=newImagePath,
                          imageFile=newImageFile,
                          imageDetailPath = newImageDetailPath,
                          imageDetailFile = newImageDetailFile)
        product.put()
        self.postRedirect()

class DeleteProduct(MainPage):
    @admin_required
    def get(self):        
        productEntry = db.get(self.request.get("product_id"))
        productEntry.delete()
        self.redirect('/CreateProduct')
        
class Products(MainPage):
    def get(self):
        uri = self.request.uri
        productsPreFix = 'Products/'
        productName = urllib.unquote(uri[uri.rfind(productsPreFix) + len(productsPreFix):])
        query = Product.gql('where name = :name', name = productName)
        productEntry  = query.get()
        if productEntry == None:
            self.error(404)
            self.response.out.write("Not found")
            return
        
        template_values = {'productEntry' : productEntry }
        self.generate('Products.html', template_values)

class ManageStore(MainPage):
    @admin_required
    def get(self):
        self.generate('ManageStore.html')
    @admin_required
    def post(self):
        newMerchantId = self.request.params['merchantId']
        newUseSandbox = self.request.params['useSandbox']
        newAboutUsDescription = self.request.params['aboutUsDescription']
        newCurentPromotion = self.request.params['currentPromotion']
        newNewsAndInfo = self.request.params['newsAndInfo']
        newTalkBox = self.request.params['talkBox']
        store = self._getDefaultStore()
        store.merchantid = newMerchantId
        store.useSandbox = newUseSandbox
        store.aboutUsDescription = newAboutUsDescription
        store.currentPromotion = newCurentPromotion
        store.newsAndInfo = newNewsAndInfo
        store.talkBox = newTalkBox
        store.put()
        self.postRedirect()
        

def main():
    application = webapp.WSGIApplication([
      ('/', MainPage),
      ('/demo', Demo),
      ('/art', Art),
      ('/ProductInfo', ProductInfo),
      ('/ContactUs', ContactUs),
      ('/AboutUs', AboutUs),
      ('/FileUpload', FileUpload),
      ('/Files/.*', DownloadFile),
      ('/DeleteFile', DeleteFile),
      ('/CreateProduct', CreateProduct),
      ('/DeleteProduct', DeleteProduct),
      ('/Administration', Administration),
      ('/Products/.*', Products),
      ('/ManageStore', ManageStore)
      ], debug=True)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
