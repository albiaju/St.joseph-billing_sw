from django.db import models
from django.utils import timezone
from accounts.models import Shop        # ← ADD


class Invoice(models.Model):
    shop = models.ForeignKey(           # ← ADD THIS FIELD
        Shop,
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    bill_number   = models.PositiveIntegerField()   # ← remove unique=True
    date          = models.DateField(default=timezone.now)
    customer_name = models.CharField(max_length=200, blank=True, default="")
    subtotal      = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cgst_amount   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sgst_amount   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount  = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_cancelled  = models.BooleanField(default=False)
    cancelled_at  = models.DateTimeField(null=True, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-bill_number']
        # Bill number unique PER SHOP (not globally)
        unique_together = ['shop', 'bill_number']

    def __str__(self):
        return f"Bill #{self.bill_number} - {self.customer_name}"


class InvoiceItem(models.Model):
    # InvoiceItem doesn't need shop — it belongs to Invoice which has shop
    invoice     = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    sl_no       = models.PositiveIntegerField()
    particulars = models.CharField(max_length=300)
    quantity    = models.DecimalField(max_digits=10, decimal_places=3)
    rate        = models.DecimalField(max_digits=10, decimal_places=2)
    amount      = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['sl_no']