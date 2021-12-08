from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("new", views.new_index, name="new_index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createlisting", views.createlist, name="createlisting"),
    path("item/<int:item_id>", views.items, name="item"),
    path("watchlist", views.watch, name="watch"),
    path("watchlist/<int:item_id>", views.watchlist, name="watchlist"),
    path("comment/<int:item_id>", views.comment, name="comment"),
    path("categories/<str:category>", views.categories, name="category"),
    path("close/<int:item_id>", views.close, name="close")
]

