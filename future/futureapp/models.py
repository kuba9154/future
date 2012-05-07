from django.db import models
from django.forms import ModelForm

class User(models.Model):
    CLASS_YEAR_CHOICES = ( 
        (u'2012', u'Senior'),
        (u'2013', u'Junior'),
        (u'2014', u'Sophomore')
    )
    ADMIN_TITLE_CHOICES = (
        (u'ME', u'Member'),
        (u'OF', u'Officer'),
        (u'FC', u'Food Chair'),
        (u'BAMF', u'Developer')
    )

    netid = models.CharField(max_length=8, unique=True)
    firstname = models.CharField("first name", max_length=30)
    lastname = models.CharField("last name", max_length=30)
    year = models.IntegerField("class year", max_length=4, choices=CLASS_YEAR_CHOICES)
    fbid = models.BigIntegerField("facebook ID",unique=True,null=True)
    authenticated = models.BooleanField("user authenticated?")
    authcode = models.CharField("authentication code", max_length=40)
    admin = models.CharField("administrator title", max_length=4, choices=ADMIN_TITLE_CHOICES)
    pic = models.CharField("facebook profile picture URL", max_length=70,blank=True)
    largepic = models.CharField("large facebook profile picture URL", max_length=70,blank=True)
    friends = models.ManyToManyField("self")
    isfriend = False
    
    
class Tag(models.Model):
    text = models.CharField("tag text", max_length=15)

# post is a superclass for many kinds of things that are posted
class Post(models.Model):
    
    author = models.ForeignKey(User)     #               verbose_name="Post Author")
    time = models.DateTimeField(auto_now_add=True)
    Tags = models.ManyToManyField(Tag)
    mentions = models.ManyToManyField(User, related_name="mentioned_posts") 
        
# general purpose user post, with a title
class UserPost(Post):
    title = models.CharField("user post title", max_length=80)
    text = models.TextField("user post text")
    hasvideo = models.BooleanField("Contains a youtube URL")
    youtubeid = models.CharField("Youtube Video Id", max_length=12, blank=True)
    announce = models.BooleanField("True if post is announcement.")
# A menu
class MenuPost(Post):
    title = models.CharField("user post title", max_length=80)
    text = models.TextField("user post text")
    # for now identical to UserPost.

# subordinate to other posts, no title
class Comment(Post):
    text = models.TextField("comment text")
    parent = models.ForeignKey(UserPost)
    
