from django.db import models
from django.utils import timezone


class Invoice(models.Model):
    """
    One row = one bill your uncle gives to a customer.
    Matches exactly the paper bill in the image.
    """
    # Bill number - auto generated, never repeats
    # Format: 21228, 21229 etc (continuing from paper bills)
    bill_number = models.PositiveIntegerField(unique=True)

    date = models.DateField(default=timezone.now)

    # Customer info
    customer_name = models.CharField(max_length=200, blank=True, default="")

    # Totals - all auto calculated when invoice is saved
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cgst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sgst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Is this bill cancelled?
    is_cancelled = models.BooleanField(default=False)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-bill_number']

    def __str__(self):
        return f"Bill #{self.bill_number} - {self.customer_name}"


class InvoiceItem(models.Model):
    """
    Each row in the bill (Sl.No, Particulars, Qty, Rate, Amount).
    One Invoice can have many InvoiceItems.
    """
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,   # if invoice deleted, items deleted too
        related_name='items'
    )

    sl_no = models.PositiveIntegerField()           # 1, 2, 3...
    particulars = models.CharField(max_length=300)  # item name/description
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # qty × rate

    class Meta:
        ordering = ['sl_no']

    def __str__(self):
        return f"{self.particulars} x {self.quantity}"