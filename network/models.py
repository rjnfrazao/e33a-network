from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

    # list_display = ('id', 'username', 'first_name', 'last_name')

    def __str__(self):
        return f"id = {self.id}, username = {self.username}, first_name = {self.first_name}, last_name = {self.last_name}"

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            #           "follows": [user.name for user in self.UserProfile.follows.all()],
        }


"""
Models to store who the user follows

"""


class Follows(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    follows = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_followed",
    )

    def __str__(self):
        return f"id = {self.id}, user = {self.user.username}, follows = {self.follows.username}"


"""
Models to store the post data

"""


class Post(models.Model):
    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="user")
    message = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user_likes = models.ManyToManyField(
        "User", related_name="user_likes", blank=True, null=True)

    def serialize(self, logged_username):

        return {
            "id": self.id,
            "username": self.user.username,
            "message": self.message,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %Z"),
            "likes": self.user_likes.count(),
            "owner": self.user.username == logged_username,
            "owner_liked": Post.objects.filter(id=self.id, user_likes__username=logged_username).count()
        }
