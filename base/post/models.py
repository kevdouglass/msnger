from django.db import models

#imports
from django.contrib.auth.models import User
import uuid

from django.db.models.signals import post_save
from django.utils.text import slugify
from django.urls import reverse


# Create your models here.
# when user creates post we want to create a folder that holds user photo, post
# user directory path django documentation

def user_directory_path(instance, filename):
    # returns the path at 
    # this file will be upleaded to MEDIA_ROOT /user(id)/filename
    return 'user_{0}/{1}'.format(instance.user.id, filename)


class Tag(models.Model):
    title = models.CharField(max_length=75, verbose_name='Tag')
    slug = models.SlugField(null=False, unique=True)
    
    
    class Meta:
        '''
            >   when user clicks on tags, call Meta then the class funcs
        '''
        verbose_name_plural='Tags'
        
    def get_absolute_url(self):
        '''
            >   When user clicks a link, this will create a url with a slug
        '''
        return reverse('tags', args=[self.slug])
    
    def __str__(self):
        ''' return the title
        '''
        return self.title
        
    def save(self, *args, **kwargs):
        ''' incase we want to change the name of the slug
        if we click save and dont have a SLUG.. we call the utility called
        Slugify and the title
        '''
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)
    
    
class Post(models.Model):
    '''
    > use UUID for django
    Model field reference: creates super long id for each post..
    import uuid to use this
    uuid4() is the most secure
    uuid1() can show user network status
    '''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    picture = models.ImageField(upload_to=user_directory_path, verbose_name='Picture', null=False)
    caption = models.TextField(max_length=1500, verbose_name='Caption')
    posted = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, related_name='tags')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.IntegerField()
    
    
    def get_absolute_url(self):
        '''
        click on post and post details.
        takes us to post details url
        '''
        return reverse('postdetail', args=[str(self.id)])
    
    # def __str__(self):
    #     return self.posted
    
    

class Follow(models.Model):
    '''
    > Tracks our User's followers
    '''
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    
class Stream(models.Model):
    '''
    >       every time we make a post, we string or make a new post to all the users that are following our User
    '''
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stream_following')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    date = models.DateTimeField()
    
    def add_post(sender, instance, *args, **kwargs):
        ''' 
            >   get this from each post, send to each person that is following 
            '''
        post = instance
        user = post.user
        # follow, get all the users that are following you
        followers = Follow.objects.all().filter(following=user)
        for follower in followers:
            stream = Stream(post=post, user= follower.follower, date=post.posted, following=user)
            stream.save()
            

#   Save posts to followers accounts everytime we make a post
post_save.connect(Stream.add_post, sender=Post)