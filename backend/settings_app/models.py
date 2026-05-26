from django.db import models


class ShopSettings(models.Model):
    """
    Stores the shop's info - shown on every invoice.
    There will only ever be ONE row in this table.
    """
    shop_name = models.CharField(max_length=200, default="ST. JOSEPH'S HARDWARES")
    address = models.TextField(default="New Extension, Madikeri - 571 201")
    mobile = models.CharField(max_length=20, default="9902237176")
    gstin = models.CharField(max_length=20, default="29ANWPD0218LIZO")
    bank_account_no = models.CharField(max_length=30, blank=True, default="348601010036056")
    bank_ifsc = models.CharField(max_length=20, blank=True, default="UBIN0900079")
    bank_name = models.CharField(max_length=100, blank=True, default="Union Bank of India, Madikeri")
    state = models.CharField(max_length=50, default="Karnataka")

    class Meta:
        verbose_name = "Shop Settings"

    def __str__(self):
        return self.shop_name