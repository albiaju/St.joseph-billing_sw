from django.db import models
from django.utils import timezone


class Purchase(models.Model):
    """
    One row = one supplier bill your uncle enters manually.
    Matches the purchase record notebook.
    """
    date = models.DateField(default=timezone.now)
    bill_number = models.CharField(max_length=100)   # supplier's bill number
    supplier_name = models.CharField(max_length=200)
    supplier_gstin = models.CharField(max_length=20, blank=True, default="")

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cgst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sgst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    loading_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    notes = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.supplier_name} - Bill #{self.bill_number}"