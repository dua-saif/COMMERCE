from django.urls import path
from . import views

from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),  # <--- This must exist
    path("create/", views.create_listing, name="create"),
    path("watchlist/", views.watchlist_view, name="watchlist"),
    path("listing/<int:listing_id>/", views.listing, name="listing"), 
    path("listing/<int:listing_id>/comment", views.add_comment, name="add_comment"),
    path("categories/", views.categories_view, name="categories"),
    path("categories/<str:category_name>/", views.category_listings, name="category_listings"),
    path("won/", views.won_auctions, name="won_auctions"),

]
