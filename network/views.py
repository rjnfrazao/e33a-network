from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

import json

from .models import User, Post, UserProfile


def index(request):
    return render(request, "network/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


"""
API to send the e-mail. This view is invoked from a javascript action associated to the submitt button (click event).
"""
@csrf_exempt
@login_required
def post(request):

    # Post a new message must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Get message of post
    data = json.loads(request.body)
    message = data.get("message", "")

    print(f"Post : {message}, by {request.user}")
    # Check of message was filled in.
    if (message == ""):
        # return error message
        return JsonResponse({
            "error": "Message content is required."
        }, status=400)
    else:
        # Add a new post.
        msg = Post(
            user=request.user,
            message=message
        )
        msg.save()
        return JsonResponse({"message": "Post published successfully."}, status=201)


"""
API to return the posts. This view is invoked from a javascript called load_posts().
"""
@csrf_exempt
@login_required
def get_posts(request):

    # Post a new message must be via POST
    if request.method != "GET":
        return JsonResponse({"error": "GET request required."}, status=400)

    # return all posts, list in reverser chronological order
    posts = Post.objects.order_by("-timestamp").all()

    # Get message of post
    return JsonResponse([post.serialize() for post in posts], safe=False)


"""
API to register the like from the user to the post.

Input : Json message 
            post_id : id from the post message to be liked.
        Request.User - User who liked the post or current user logged.
"""
@csrf_exempt
@login_required
def like(request):
    return JsonResponse({"message": "Like added successfully."}, status=201)


"""
API to add a new user to be followed.

Input : Json message 
            user_followed : user id to be followed.
        Request.User - User following or current user logged.
"""
@csrf_exempt
@login_required
def follow(request):
    return JsonResponse({"message": "User been followed successfully."}, status=201)
