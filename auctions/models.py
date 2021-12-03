from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE


CATEGORY_CHOICES = [
    ("No Category", 'No Category'),
    ("Cars", 'Cars'),
    ("Fathion", 'Fathion'),
    ("Sport", 'Sport'),
    ("Electronics", 'Electronics'),
]


class User(AbstractUser):
    watchlist = models.ManyToManyField(
        "Auctions", blank=True, related_name="user_watch")


class Auctions(models.Model):
    category = models.CharField(
        max_length=12,
        choices=CATEGORY_CHOICES,
        default=CATEGORY_CHOICES[0],
    )

    name = models.CharField(max_length=64)
    description = models.CharField(max_length=200)
    startbid = models.IntegerField()
    img = models.ImageField(upload_to="images", blank=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_auction")
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ,Current Bid ${self.startbid}.Description: {self.description}"


class Bids(models.Model):
    auction = models.ForeignKey(
        Auctions, on_delete=models.CASCADE, related_name="bid")
    bid = models.IntegerField()
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_bid")

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="startbid_greater_than_bid",
                check=models.Q(bid__lte=models.F("bid")),
            ),
        ]

    def __str__(self):
        return f"{self.user} Bids with {self.bid}"


class Comments(models.Model):
    auction = models.ForeignKey(
        Auctions, on_delete=models.CASCADE, related_name="auction_comment")
    comment = models.CharField(max_length=200)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_comment")

    def __str__(self):
        return f"{self.user}: {self.comment}"
