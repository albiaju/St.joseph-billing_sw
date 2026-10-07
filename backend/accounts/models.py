from django.db import models
from django.contrib.auth.models import User


class Shop(models.Model):
    """
    Links a Django user account to a shop.
    Uncle has 2 users → 2 Shop rows → 2 completely separate datasets.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='shop'
    )
    shop_name = models.CharField(max_length=200)
    address = models.TextField(default="")
    mobile = models.CharField(max_length=20, default="")
    gstin = models.CharField(max_length=20, default="")
    bank_account_no = models.CharField(max_length=30, blank=True, default="")
    bank_ifsc = models.CharField(max_length=20, blank=True, default="")
    bank_name = models.CharField(max_length=100, blank=True, default="")

    def __str__(self):
        return f"{self.shop_name} ({self.user.username})"