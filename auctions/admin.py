from django.contrib import admin
from .models import Listing, Bid, Comment, User

admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(User)