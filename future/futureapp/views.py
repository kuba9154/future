from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from models import *

# Create your views here.

# Render homepage with posts from DB:
def renderHomepage(request):
   now = datetime.now()
   posts = UserPost.objects.all();

   c = RequestContext(request, {'post_list':posts})
   return render_to_response('home.html', c)


# make a post.
def post(request):
    if request.method == 'POST':
        newPost = UserPost(title = 'foo', #title=request.POST['title'],
                     text = request.POST['text'],
                     #author = request.session['userid'],
        #             tags = (),
        #             mentions = ()
                          )
        newPost.save()
        return HttpResponse(newPost.text)
    else:
        return HttpResponse('SOMETHING IS WRONG.')

        


