from django.db import models
from django.utils import timezone
from markdownx.models import MarkdownxField
from .utils import markdownify
from django.contrib.auth.models import User
#from django.db.models.signals import post_save
from django.dispatch import receiver
#from django.utils.text import slugify
from slugify import slugify

STATUS = (
        (0,"Draft"),
        (1,"Publish")
)


class Blog(models.Model):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=False)
    #date = models.DateTimeField(default=timezone.now)
    date = models.DateTimeField(auto_now_add=True)
    description = MarkdownxField()
    #date_published = models.DateTimeField(blank=True, null=True)
    date_updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUS, default=0)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
            self.slug = slugify(self.title)
            self.status = 1
            super().save(*args, **kwargs)

    def formatted_markdown(self):
        return markdownify(self.description)

class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE,related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return 'Comment {} by {}'.format(self.body, self.name)

#    def publish(self):
#        self.published_date = timezone.now()
#        self.save()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_bio = models.TextField()
    signup_confirmation = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

@receiver(models.signals.post_save, sender=User)
def update_profile_signal(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
