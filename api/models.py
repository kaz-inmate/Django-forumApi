from django.db import models
from django.conf import settings
import uuid 
from django.contrib.contenttypes.models import ContentType 
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models import F 
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from rest_framework.authtoken.models import Token

class BaseModel(models.Model):
    eid = models.UUIDField(primary_key= True, default= uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)


    class Meta: abstract = True


class Votable(BaseModel):
    upvote_count = models.PositiveIntegerField(default=0)
    downvote_count = models.PositiveIntegerField(default=0)

    class Meta: abstract = True

    def get_score(self):
        return self.upvote_count - self.downvote_count


#  ------------ model for Posts --------

class Post(Votable):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name= 'posts_submitted', on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='uploads/%Y/%m/%d/', blank=True, null=True)
    comment_count = models.PositiveIntegerField(default=0)

    def childern(self):
        return self.comments.filter(parent=None)


    def __str__(self):
        return str(self.eid) + ": " + self.title


# -----------model for comments---------------
class Comment(Votable):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='comments_author', on_delete=models.CASCADE)
    text = models.TextField()
    parent = models.ForeignKey('self', related_name='children', null=True, blank=True, on_delete=models.CASCADE)


    def __str__(self):
        return str(self.eid + ": " + self.text)



# ---------- voting -----------

class UserVote(BaseModel):
    UP_VOTE = 'U'
    DOWN_VOTE = 'D'
    VOTE_TYPE = (
        (UP_VOTE, 'Up Vote'),
        (DOWN_VOTE, 'Down Vote')
    )

    voter = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='votes', on_delete=models.CASCADE)

    #----- getneric foreign key config

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')


    vote_type = models.CharField(max_length=1, choices=VOTE_TYPE)

    class Meta: unique_together = ['voter', 'object_id', 'content_type']



# ------------increase comment count ----------

@receiver(post_save, sender=Comment, dispatch_uid='comment_added')
def comment_added(sender, instance, **kwargs):
    created = kwargs.pop('created')
    post = instance.post
    if created:
        post.comment_count = F('comment_count') + 1
        post.save()


@receiver(post_save, sender=UserVote, dispatch_uid='user_voted')
def user_voted(sender, instance, **kwargs):
    created = kwargs.pop('created')
    content_obj = instance.content_object

    #the user is voting for the first time

    if created:
        if instance.vote_type == UserVote.UP_VOTE:
            content_obj.change_upvote_count(1)
        else:
            content_obj.change_downvote_count(1)

    
    #the user has switched votes

    else:
        #the previous vote was downvote but now upvotec
        if instance.vote_type == User.UP_VOTE:
            content_obj.change_upvote_count(1)
            content_obj.change_downvote_count(-1)
        else:
            content_obj.change_upvote_count(-1)
            content_obj.change_downvote_count(1)



@receiver(post_delete, sender=UserVote, dispatch_uid='user_vote_deleted')
def user_vote_deleted(sender, instance, **kwargs):
    content_obj = instance.content_obj

    if instance.vote_type == UserVote.UP_VOTE:
        content_obj.change_upvote_count(-1)
    else:
        content_obj.change_downvote_count(-1)

# ------------------ save user token once registered -------

@receiver(post_save, sender= settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)