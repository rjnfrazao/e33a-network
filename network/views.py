from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

import json

from .models import User, Post, Follows

# Global Variables
gbl_page_size = 10      # page size for the number o post to be displayed

#
# Function return the json element to be returned, so javascript knows how render navigation buttons.
# Parameter - count : number of records of the dataset, offset - current offset to be displayed.


def pages(count, offset):

    previous = -1
    next = -1

    pages = {"count": count, "offset": offset, "previous": -1, "next": -1}

    if count == 0:
        # no records return default page, no previous no next button
        return pages

    previous = offset-gbl_page_size         # previous offset
    next = offset+gbl_page_size             # next offset
    pages["previous"] = previous
    pages["next"] = next

    if next >= count:
        # if next bigger than count, hide next button
        pages["next"] = -1
    if previous < 0:
        # hide previous button
        pages["previous"] = -1

    return pages


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
API to post the message.
"""
@csrf_exempt
@login_required
def save_post(request):

    # Post a new message must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Get message of post
    data = json.loads(request.body)
    message = data.get("message", "")

    # print(f"Post : {message}, by {request.user}")
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
API to update the post.
"""
@csrf_exempt
@login_required
def upd_post(request):

    # Post a new message must be via PUT
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)

    # Get message of post
    data = json.loads(request.body)
    id_post = data.get("id_post", "")
    message = data.get("message", "")

    # print(f"Post : {message}, by {request.user}")
    # Check of message was filled in.
    if (message == ""):
        # return error message
        return JsonResponse({
            "error": "Message content is required."
        }, status=400)
    else:
        post = Post.objects.get(id=id_post)
        if post.user != request.user:
            return JsonResponse({
                "error": "Wrong user."
            }, status=400)
        # Update the post.
        post.message = message
        post.save()
        return JsonResponse({"message": "Post published successfully."}, status=201)


"""
API to return the posts. This view is invoked from a javascript called load_posts().
Return post in JSON format, ordered by timestamp in descendent order.

Input : username (GET param) - Used to filter posts by username, but when blank returns all posts.
"""
@csrf_exempt
@login_required
def get_posts(request):

        # check if get method
    if request.method != "GET":
        return JsonResponse({"error": "GET request required."}, status=400)

    # Compare user name with current user.
    try:
        username = ""
        f_flag = False
        offset = int(request.GET["offset"])
        try:
            f_flag = request.GET["f_flag"]
        except:
            username = request.GET["username"]

        if f_flag:
            # returs posts from users which the logged user follows
            # { id, username, message, timestamp, likes }
            count = Post.objects.order_by("-timestamp").filter(
                user__user_followed__user=request.user).count()
            limit = offset + gbl_page_size
            posts = Post.objects.order_by("-timestamp").filter(
                user__user_followed__user=request.user)[offset:limit]
        elif username == "":
            # return all posts, if parameter username is empty.
            # return in reverser chronological order
            count = Post.objects.order_by("-timestamp").all().count()
            limit = offset + gbl_page_size
            posts = Post.objects.order_by("-timestamp").all()[offset:limit]
        else:
            # Get user´s posts
            # posts = Post.objects.order_by(
            #    "-timestamp").filter(user__username=username)[offset:10]  # return in reverser chronological order
            # return JsonResponse([post.serialize() for post in posts], safe=False)
            count = Post.objects.order_by(
                "-timestamp").filter(user__username=username).count()              # total of records
            limit = offset + gbl_page_size
            posts = Post.objects.order_by(
                "-timestamp").filter(user__username=username)[offset:limit]  # return in reverser chronological order

        posts = [post.serialize(request.user.username) for post in posts]
        response = {}
        try:
            # Add Pages info to the response to implement pagination.
            response["pages"] = pages(count, offset)
        except:
            pass
        response["posts"] = posts
        # print(response)
        return JsonResponse(response, safe=False)
    except:
        return JsonResponse({"API get_posts error": "Undefined error, when returning posts"}, status=400)


"""
API to return the user profile. This view is invoked from a javascript called load_profile().
Return profile in JSON format.

Input : username (GET param) - Used to get the profile by username.
"""
@csrf_exempt
@login_required
def get_profile(request):

    # check if get method
    if request.method != "GET":
        return JsonResponse({"error": "GET request required."}, status=400)

    # Compare user name with current user.
    try:
        # Return user's data
        get_username = request.GET["username"]
        user_profile = User.objects.get(username=get_username)

        # Count follows and followed
        follows = Follows.objects.filter(
            user=user_profile).count()  # number of follows
        followed = Follows.objects.filter(
            follows=user_profile).count()  # number of followed

        # Logic to display button follow (not following), unfollow (already following), or hide it (same user).
        button = ""
        if get_username == request.user.username:
            button = "Hide"
        else:
            #print(f'get username:{get_username}, logged user:{request.user.username}')
            q = Follows.objects.filter(
                user=request.user, follows__username=get_username).count()
            if q == 0:
                button = "Follow"
            else:
                button = "Unfollow"

        # Json data to return are user data + additional information
        user_dict = user_profile.serialize()
        user_dict.update({'follows': follows})
        user_dict.update({'followed': followed})

        # Displays button follow, unfollow, or hide it
        user_dict.update({'btnFollow': button})

        # user_data = {**user, {'follows': follows}, {'followed': followed}}
        # print(f'follows:{follows}, followed:{followed}')
        return JsonResponse(user_dict, safe=False)

    except:
        return JsonResponse({"Internal error": "Loading profile."}, status=400)


"""
API to register the like from the user to the post.

Input : Json message
            post_id : id from the post message to be liked.
        Request.User - User who liked the post or current user logged.
"""
@csrf_exempt
@login_required
def upd_like(request):

    # Post a new message must be via PUT
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)

    try:
        # Get message of post
        data = json.loads(request.body)
        id_post = data.get("id_post", "")
        oper = data.get("oper", "")

        # get the post to be liked or unliked
        post = Post.objects.get(id=id_post)

        if (oper == "liked"):
            # operations is to add a like from the logged user
            post.user_likes.add(request.user)
        else:
            # operations is unlike the logged user from the postp
            post.user_likes.remove(request.user)

        return JsonResponse({"message": "Like updated successfully."}, status=201)
    except:
        return JsonResponse({"Internal error": "Error processing like."}, status=400)


"""
API to a user follow or unfollow another. Request.User - logged user is always following or unfollowing someone else.

Input : Json message
        user_followed : user id to be followed or unfollowed.
        oper : "follow" or "unfollow"
"""
@csrf_exempt
@login_required
def upd_follow(request):

   # Post a new message must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    try:
        # Get message of post
        data = json.loads(request.body)
        id_following = request.user.id
        oper = data.get("oper", "")

        id_followed = data.get("user_followed", "")
        # f_user is the user to be followed or unfollowed
        f_user = User.objects.get(id=id_followed)

        # print(f"User : {id_following}, followed: {id_followed}, oper: {oper}")
        # Check operation
        if (oper == "Follow"):
            # follow
            follow = Follows(
                user=request.user,          # logged user
                follows=f_user              # user to be unfollowed
            )
            follow.save()
            return JsonResponse({"message": "Follows successfully."}, status=201)
        else:
            # unfollow
            follow = Follows.objects.get(
                user=request.user, follows=f_user)      # logged user, user to be followed
            follow.delete()
            return JsonResponse({"message": "Unfollowed successfully."}, status=201)

        return JsonResponse({"message": "User been followed successfully."}, status=201)
    except:
        return JsonResponse({"Internal error": "Error processing follow / unfollow."}, status=400)
