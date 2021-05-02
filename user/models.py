from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Post(models.Model):
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    inbox_url = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.content


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='sayit_profile_pictures')


class Inbox(models.Model):
    user = models.ForeignKey('Profile', on_delete=models.CASCADE)
    inbox_counter = models.AutoField(primary_key=True)
    inbox_url = models.CharField(max_length=100,null=True,blank=True)
    inbox_name = models.CharField(max_length=20)

