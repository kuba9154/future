from django.db import models
from django.forms import ModelForm

# A user of the Web F. Site
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

    # Basic user information
    netid = models.CharField(max_length=8, unique=True)
    firstname = models.CharField("first name", max_length=30)
    lastname = models.CharField("last name", max_length=30)
    year = models.IntegerField("class year", max_length=4, choices=CLASS_YEAR_CHOICES)
    
    # User's facebook id, a unique integer, also used as our
    # authentication hook when a user visits the site
    fbid = models.BigIntegerField("facebook ID",unique=True,null=True)
    
    # Information for authenticating new users. Code must be provided
    # to match netids with facebook accounts, verifying identity.
    authenticated = models.BooleanField("user authenticated?")
    authcode = models.CharField("authentication code", max_length=40)
    
    # Permissions of the user for administrative purposes
    admin = models.CharField("administrator title", max_length=4, choices=ADMIN_TITLE_CHOICES)
    
    # URLS for different sizes of pictures, pulled from facebook's cdn
    # for now
    pic = models.CharField("facebook profile picture URL", max_length=70,blank=True)
    largepic = models.CharField("large facebook profile picture URL", max_length=70,blank=True)
    
    #  Internal database representation of facebook friend relationship
    friends = models.ManyToManyField("self")
    isfriend = False # rendered at page display time for access in
    # template language using the friends many to many relationship    

# A tag is a hashtag, consisting of a short amount of text and linked
# to posts by a many to many relationship where each post can have
# many tags and each tag can tag many posts
class Tag(models.Model):
    text = models.CharField("tag text", max_length=24)
    time = models.DateTimeField(auto_now_add=True)

# Post here is a superclass for many kinds of things that are posted,
# containing fields that are used in multiple types
class Post(models.Model):
    
    author = models.ForeignKey(User)
    text = models.TextField("post text")
    time = models.DateTimeField(auto_now_add=True)
    Tags = models.ManyToManyField(Tag)
    mentions = models.ManyToManyField(User, related_name="mentioned_posts") 
    hasvideo = models.BooleanField("Contains a youtube URL")
    youtubeid = models.CharField("Youtube Video Id", max_length=12, blank=True)
        
# A general purpose post, the main type of social content on the site
class UserPost(Post):
    announce = models.BooleanField("True if post is announcement.")
    
# A menu, no special information for now
class MenuPost(Post):
    pass

# A comment, subordinate to other posts
class Comment(Post):
    parent = models.ForeignKey(UserPost)    
