from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "follows": [user.name for user in self.UserProfile.follows.all()],
        }


"""
Models to store user´s additional data

"""


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    follows = models.ManyToManyField("User", related_name="user_follows")


"""
Models to store the post data

"""


class Post(models.Model):
    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="user")
    message = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user_likes = models.ManyToManyField("User", related_name="user_likes")
    likes = models.IntegerField(default=0)

    def serialize(self):
        return {
            "id": self.id,
            "username": self.user.username,
            "message": self.message,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %Z"),
            "likes": self.likes,
        }
