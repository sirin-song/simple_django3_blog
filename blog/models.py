from django.db import models
from django.utils import timezone
from markdownx.models import MarkdownxField
from .utils import markdownify
from django.contrib.auth.models import User
#from django.db.models.signals import post_save
from django.dispatch import receiver

class Blog(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateTimeField(default=timezone.now)
    description = MarkdownxField()
    date_published = models.DateTimeField(blank=True, null=True)
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def formatted_markdown(self):
        return markdownify(self.description)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
#    first_name = models.CharField(max_length=100, blank=True)
#    last_name = models.CharField(max_length=100, blank=True)
#    email = models.EmailField(max_length=150)
    user_bio = models.TextField()
    signup_confirmation = models.BooleanField(default=False)
#
    def __str__(self):
        return self.user.username

@receiver(models.signals.post_save, sender=User)
def update_profile_signal(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()