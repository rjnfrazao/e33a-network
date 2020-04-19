from django.contrib import admin
from.models import User, Follows, Post

# Register your models here.

admin.site.register(User)
admin.site.register(Follows)
admin.site.register(Post)
