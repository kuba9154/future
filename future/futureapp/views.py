from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render_to_response,redirect
from django.template import RequestContext
from urllib import quote
from models import *
from os import getenv
from django.conf import settings
import string
from random import choice
import requests
from facepy import GraphAPI
from datetime import datetime, timedelta
# Create your views here.

# Render homepage with posts from DB:
def renderHomepage(request):
   # check that user is logged in:
   if request.session.get('logged_in'):
       posts = UserPost.objects.order_by('-time')
       curUser = User.objects.filter(pk = request.session['uid'])
       curUser = curUser[0]    #querydict
       c = RequestContext(request, {'post_list':posts,
               'curUser':curUser,})
       return render_to_response('home.html', c)
   else:
       return redirect('/fbauth/')
   
# renders the directory page
def directory(request):
   if request.session.get('logged_in'):
       members = User.objects.all();
       curUser = User.objects.filter(pk = request.session['uid'])
       curUser = curUser[0]    #querydict
       c = RequestContext(request, {'member_list':members,
                                'curUser':curUser})
       return render_to_response('directory.html', c)
   else:
       return redirect('/fbauth/')
   
# render the menu page:
def renderMenu(request):
   if request.session.get('logged_in'):
       # get curUser:
       members = User.objects.all();
       curUser = User.objects.filter(pk = request.session['uid'])
       curUser = curUser[0]    #querydict
       # determine post access:
       a = curUser.admin
       if(a == u'FC' or a == u'BAMF'):
           postPerm = True;
       else:
           postPerm = False;
       # get all menu posts:
       menus = MenuPost.objects.order_by('-time')

       c = RequestContext(request, {'menu_list':menus,
               'curUser':curUser, 'postPerm':postPerm})
       return render_to_response('menu.html', c)
   else:
       return redirect('/fbauth/')


# ----      Menu Manipulation       ----#

# make a new menu
def postMenu(request):
    if request.method == 'POST':
        #get curuser
        curAuthor = User.objects.filter(pk = request.session['uid'])
        curAuthor = curAuthor[0]    #it's a querydict
        # check permissions
        a = curAuthor.admin
        if(a == u'FC' or a == u'BAMF'):
            newMenu = MenuPost(title = 'foo', #title=request.POST['title'],
                               text = request.POST['text'],
                               author = curAuthor,
                 #             tags = (),
                 #             mentions = ()
                                             )
            newMenu.save()
            return renderMenu(request) 
        else:
            return HttpResponse('You do not have permission to post menus.') 
    else:
        # we need to change this to a more general-purpose error.
        # Control flow reaches here if the user tries to go to the posting url
        # without actually making a post.
        return HttpResponse('Menu Posting failed!')

#delete a menu:
def deleteMenu(request):
    if request.method == 'POST':
        #check author
        curUser = User.objects.filter(pk = request.session['uid'])
        curUser = curUser[0]    #querydict
        # check permissions
        a = curUser.admin
        if(a == u'FC' or a == u'BAMF'):
            id = request.POST['postMenu']
            p = MenuPost.objects.get(pk = id)
            p.delete()
            return renderMenu(request)
        else:
            return HttpResponse('You do not have permission to delete menus.') 
    else:
        return HttpResponse('Menu deletion failed!')


# ----      UserPost Manipulation       ----#

# make a new UserPost.
def post(request):
    if request.method == 'POST':
        curAuthor = User.objects.filter(pk = request.session['uid'])
        curAuthor = curAuthor[0]    #it's a querydict
        newPost = UserPost(title = 'foo', #title=request.POST['title'],
                     text = request.POST['text'],
                     author = curAuthor,
        #             tags = (),
        #             mentions = ()
                          )
        newPost.save()
        return renderHomepage(request) 
    else:
        # we need to change this to a more general-purpose error.
        # Control flow reaches here if the user tries to go to the posting url
        # without actually making a post.
        return HttpResponse('Posting failed!')

#delete a UserPost:
def deletePost(request):
    if request.method == 'POST':
        #check author
        curUser = User.objects.filter(pk = request.session['uid'])
        curUser = curUser[0]    #querydict

        id = request.POST['post']
        p = UserPost.objects.get(pk = id)
        if p.author == curUser or curUser.admin == 'BAMF':
            p.delete()
            return renderHomepage(request)
        else:
            return HttpResponse('You may not delete a post you do not own.')
    else:
        return HttpResponse('Post deletion failed!')

# ----      Authentication       ---- #

# Authenticate user's netid
def signup(request):
    
   # this page should not be accessed by any method other than GET
   if request.method != 'GET':
       return HttpResponse(status=405)
       
   requestnetid = request.GET.get('netid', '')
   if requestnetid == '': # Http GET request has no netid parameter
      return HttpResponse('not a valid signup request')
       
   signup_user = User.objects.filter(netid = requestnetid)
   if signup_user.count() == 0: # netid not found in database
      return HttpResponse('netid not approved for signup')
        
   signup_user = signup_user[0]
   if signup_user.authenticated == True:
      return HttpResponse('netid already authenticated')
   
   # provided code does not match code in database or parameter is empty
   if request.GET.get('code', '') != signup_user.authcode:
      return HttpResponse('Please check that signup link is correct, contains incorrect authentication code')
   
   return HttpResponse('OH YEAHHHHH!')

# does facebook authentication.
def fbauth(request):
   # The url for this page, to be passed as a param to facebook for redirection
   facebookredirect = settings.BASE_URI + 'fbauth/'
   facebookredirect = quote(facebookredirect, '')
   
   # if the incoming request is a redirect from facebook with a code
   # that may be exchanged for an oauth token
   if request.method == 'GET':
      
      # if already has an active facebook session
      if request.session.get('fb_token', '') != '':
         
         # if the token is not expired, else fall through to acquire a
         # new one
         if request.session.get('fb_expiry', datetime.now()) > datetime.now():
            
            # if logged in (probably reached this page by accident)
            if request.session.get('logged_in', False):
               return renderHomepage(request)

            # if not logged in, look through the database for the fbid in
            # the session
            else:
               graph = GraphAPI(request.session['fb_token'])
               visitor_fbid = int(graph.get('me')['id'])
               #return HttpResponse(str(visitor_fbid))
               this_user = User.objects.filter(fbid = visitor_fbid)
               if this_user.count() == 0: # if fbid not in db
                  request.session['approved_fb'] = True
                  return redirect('/netidauth/')
               else: # if fbid in db already
                  this_user = this_user[0]
                  this_user.pic = 'https://graph.facebook.com/' + str(visitor_fbid) + '/picture?type=square'
                  this_user.save()
                  request.session['logged_in'] = True
                  request.session['uid'] = this_user.pk
                  return renderHomepage(request)
      
      # if this is a response from facebook with a code to grab a csrf token
      if request.GET.get('code', '') != '' and request.session['fb_csrf']:
         # Check that the request has a valid csrf token that matches
         # the one stored in the session
         if request.session['fb_csrf'] == request.GET.get('state', ''):
            
            # Create a url to exchange the code received for an oauth token
            oauthurl = 'https://graph.facebook.com/oauth/access_token?'
            
            # Add the fb app ID
            oauthurl += 'client_id='
            oauthurl += settings.FACEBOOK_APP_ID
            
            # Add a redirect url, which should point back to this page
            oauthurl += '&redirect_uri='
            oauthurl += facebookredirect
            
            # Add our app's secret, from developer.facebook.com
            oauthurl += '&client_secret='
            oauthurl += settings.FACEBOOK_API_SECRET
            
            oauthurl += '&code='
            oauthurl += request.GET['code']
            
            gettoken = requests.get(oauthurl)
            
            # Body is of format token and expiry time, split into
            # appropriate parts
            tokenized = gettoken.text.split('&')
            token = tokenized[0].split('=')[1]
            expiry = int(tokenized[1].split('=')[1])
            request.session['fb_token'] = token
            request.session['fb_expiry'] = datetime.now() + timedelta(seconds = expiry)
            #return HttpResponse('sup')
            return redirect('/fbauth/')

      # Create an initial facebook authentication redirect url, a la 
      # https://developers.facebook.com/docs/authentication/server-side/
      facebookurl = 'https://www.facebook.com/dialog/oauth?'
      
      # Add the facebook app ID
      facebookurl += 'client_id='
      facebookurl += settings.FACEBOOK_APP_ID
      
      # Add a redirect url, which must be the same as one indicated in
      # the fb app settings
      facebookurl += '&redirect_uri='
      facebookurl += facebookredirect
      
      # don't think we need additional permissions for now, but if we do,
      # later can uncomment these lines. see 
      # https://developers.facebook.com/docs/authentication/permissions/
      #facebookurl += '&scope='
      #facebookurl += COMMA_SEPARATED_LIST_OF_PERMISSION_NAMES
      
      # To protect against CSRF, add a key which is then checked later
      facebookurl += '&state='
      fb_csrf = "".join([choice(string.letters+string.digits) for x in range(1, 40)])
      request.session['fb_csrf'] = fb_csrf
      facebookurl += fb_csrf
      
      return redirect(facebookurl)

   # this page should not be accessed through any method but GET
   else:
      return HttpResponse(status=405)
