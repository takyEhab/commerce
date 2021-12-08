from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required

from .models import Auctions, Bids, Comments, User, CATEGORY_CHOICES


class CreateList(forms.Form):

    title = forms.CharField(label="List Title", max_length=64)
    description = forms.CharField(widget=forms.Textarea)
    category = forms.CharField(
        label='Category', widget=forms.Select(choices=CATEGORY_CHOICES))
    startBid = forms.IntegerField(label="Starting Bid")
    img = forms.ImageField(required=False)


class Bid(forms.Form):
    bid = forms.IntegerField(label="Bid")


class Comment(forms.Form):
    comment = forms.CharField(widget=forms.Textarea)


def index(request):
    auc = Auctions
    return render(request, "auctions/index.html", {
        "auctions": auc.objects.all()
    })


def new_index(request):
    return render(request, "auctions/new_index.html")


@login_required(redirect_field_name=None, login_url="login")
def createlist(request):
    if request.method == 'POST':
        form = CreateList(request.POST, request.FILES)

        if form.is_valid():

            title = form.cleaned_data["title"]
            startbid = form.cleaned_data["startBid"]
            description = form.cleaned_data["description"]
            category = form.cleaned_data["category"]
            img = form.cleaned_data["img"]

            username = Auctions(name=title, startbid=startbid, description=description,
                                category=category, img=img, user=request.user)
            username.save()

            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, "auctions/createlisting.html", {
                "form": form
            })

    else:
        return render(request, "auctions/createlisting.html", {
            "form": CreateList()
        })


def items(request, item_id):
    item = Auctions.objects.get(pk=item_id)
    users = item.user_watch.all()
    user = request.user
    context = {}

    win = item.bid.last()
    context["winner"] = win

    context["item"] = item
    context["form"] = Bid()
    context["comment_form"] = Comment()

    comments = item.auction_comment.all()
    context["comments"] = comments

    if request.method == 'GET':
        if user in users:
            context["message"] = "Remove Watch list"

        else:
            context["message"] = "Add to watch list"

        return render(request, "auctions/item.html", context)

    else:

        form = Bid(request.POST)

        if form.is_valid():

            bid = form.cleaned_data["bid"]

            if bid > item.startbid:
                user = Bids(auction=item, bid=bid, user=request.user)
                user.save()
                item.startbid = bid
                item.save()
                return HttpResponseRedirect(reverse("item", kwargs={'item_id': item_id}))
            else:
                context["error"] = "The bid must be more than the current price"
                return render(request, "auctions/item.html", context)

        else:
            context["form"] = form
            return render(request, "auctions/item.html", context)


@login_required(redirect_field_name=None, login_url="login")
def comment(request, item_id):
    item = Auctions.objects.get(pk=item_id)

    if request.method == "POST":
        Comment_form = Comment(request.POST)

        if Comment_form.is_valid():
            comment = Comment_form.cleaned_data["comment"]
            user_comment = Comments(
                comment=comment, auction=item, user=request.user)
            user_comment.save()

            return HttpResponseRedirect(reverse("item", kwargs={'item_id': item_id}))

        else:
            return HttpResponseRedirect(reverse("item", kwargs={'item_id': item_id}))


def categories(request, category):
    items = Auctions.objects.all()

    if [item for item in CATEGORY_CHOICES if category in item]:
        return render(request, "auctions/category.html", {
            "category": category,
            "items": items
        })
    else:
        return render(request, "auctions/error.html", {
            "message": "No category found"
        })


@login_required(redirect_field_name=None, login_url="login")
def watch(request):
    items = request.user.watchlist.all()
    return render(request, "auctions/watch.html", {
        "items": items
    })


@login_required(redirect_field_name=None, login_url="login")
def watchlist(request, item_id):
    item = Auctions.objects.get(pk=item_id)
    it = item.user_watch.all()
    user = request.user

    if request.GET["q"] == "a":
        user.watchlist.add(item_id)
        return HttpResponseRedirect(reverse("item", kwargs={'item_id': item_id}))
    else:
        user.watchlist.remove(item_id)
        return HttpResponseRedirect(reverse("item", kwargs={'item_id': item_id}))


def close(request, item_id):
    item = Auctions.objects.get(pk=item_id)
    if request.user == item.user:
        item.active = False
        item.save()
    return HttpResponseRedirect(reverse("item", kwargs={'item_id': item_id}))


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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
