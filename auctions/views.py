from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db import IntegrityError

from .models import Listing, Bid, Comment, User
from .forms import ListingForm

def index(request):
    listings = Listing.objects.filter(is_active=True)

    current_prices = {}
    for listing in listings:
        highest_bid = listing.bids.order_by('-amount').first()
        current_prices[listing.id] = highest_bid.amount if highest_bid else listing.starting_bid

    return render(request, "auctions/index.html", {
        "listings": listings,
        "current_prices": current_prices
    })

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

def logout_view(request):
    logout(request)
    return redirect(reverse("index"))

@login_required
def create_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.save()
            messages.success(request, "Listing created successfully!")
            return redirect("index")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ListingForm()
    return render(request, "auctions/create.html", {"form": form})

def listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    bids = listing.bids.all().order_by('-amount')
    comments = listing.comments.all()
    current_price = bids[0].amount if bids.exists() else listing.starting_bid

    if request.method == "POST" and request.user.is_authenticated:
        if "bid" in request.POST:
            try:
                bid_amount = float(request.POST["bid"])
                if bid_amount <= current_price:
                    messages.error(request, "Your bid must be greater than the current price.")
                else:
                    Bid.objects.create(bidder=request.user, listing=listing, amount=bid_amount)
                    messages.success(request, "Your bid has been placed successfully.")
                    return redirect("listing", listing_id=listing_id)
            except ValueError:
                messages.error(request, "Invalid bid format.")
                return redirect("listing", listing_id=listing_id)

        elif "watchlist" in request.POST:
            if listing in request.user.watchlist.all():
                request.user.watchlist.remove(listing)
                messages.success(request, "Removed from your watchlist.")
            else:
                request.user.watchlist.add(listing)
                messages.success(request, "Added to your watchlist.")
            return redirect("listing", listing_id=listing_id)

        elif "close_auction" in request.POST:
            if request.user == listing.owner:
                listing.is_active = False
                highest_bid = listing.bids.order_by('-amount').first()
                if highest_bid:
                    listing.winner = highest_bid.bidder
                listing.save()
                messages.success(request, "You have closed the auction.")
            return redirect("listing", listing_id=listing_id)

        elif "reopen_auction" in request.POST:
            if request.user == listing.owner:
                listing.is_active = True
                listing.winner = None
                listing.save()
                messages.success(request, "You have reopened the auction.")
            return redirect("listing", listing_id=listing_id)

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bids": bids,
        "comments": comments,
        "current_price": current_price,
    })

def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirmation = request.POST.get("confirmation")

        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })

        login(request, user)
        return redirect(reverse("index"))

    return render(request, "auctions/register.html")

@login_required
def watchlist_view(request):
    user_watchlist = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "watchlist": user_watchlist
    })

@login_required
def add_comment(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    if request.method == "POST":
        content = request.POST.get("comment_content", "").strip()
        if content:
            Comment.objects.create(commenter=request.user, listing=listing, content=content)
            messages.success(request, "Your comment has been added.")
        else:
            messages.error(request, "Comment cannot be empty.")
    return redirect("listing", listing_id=listing_id)

def categories_view(request):
    categories = Listing.objects.filter(is_active=True).values_list('category', flat=True).distinct()
    categories = [cat for cat in categories if cat]
    return render(request, "auctions/categories.html", {
        "categories": categories
    })

def category_listings(request, category_name):
    listings = Listing.objects.filter(category=category_name, is_active=True)

    current_prices = {}
    for listing in listings:
        highest_bid = listing.bids.order_by('-amount').first()
        current_prices[listing.id] = highest_bid.amount if highest_bid else listing.starting_bid

    return render(request, "auctions/category_listings.html", {
        "category_name": category_name,
        "listings": listings,
        "current_prices": current_prices
    })


def won_auctions(request):
    if not request.user.is_authenticated:
        return render(request, "auctions/won_auctions.html", {
            "error_message": "Please log in to see your won auctions."
        })

    listings = Listing.objects.filter(winner=request.user)

    final_prices = {}
    for listing in listings:
        highest_bid = listing.bids.order_by('-amount').first()
        final_prices[listing.id] = highest_bid.amount if highest_bid else listing.starting_bid

    return render(request, "auctions/won_auctions.html", {
        "listings": listings,
        "final_prices": final_prices
    })
