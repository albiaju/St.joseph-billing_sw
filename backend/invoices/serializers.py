from rest_framework import serializers
from .models import Invoice, InvoiceItem
from num2words import num2words


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ['id', 'sl_no', 'particulars', 'quantity', 'rate', 'amount']
        # sl_no and amount are auto-generated, so make them read-only
        read_only_fields = ['id', 'sl_no', 'amount']


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True)
    total_in_words = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            'id', 'bill_number', 'date', 'customer_name',
            'subtotal', 'cgst_amount', 'sgst_amount', 'total_amount',
            'is_cancelled', 'items', 'total_in_words', 'created_at'
        ]
        # bill_number and totals are auto-generated, not sent by frontend
        read_only_fields = [
            'id', 'bill_number', 'subtotal', 'cgst_amount',
            'sgst_amount', 'total_amount', 'is_cancelled', 'created_at'
        ]

    def get_total_in_words(self, obj):
        try:
            rupees = int(obj.total_amount)
            paise = round((float(obj.total_amount) - rupees) * 100)
            words = num2words(rupees, lang='en_IN').title()
            if paise > 0:
                paise_words = num2words(paise, lang='en_IN').title()
                return f"{words} Rupees And {paise_words} Paise Only"
            return f"{words} Rupees Only"
        except:
            return ""

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        shop = self.context['shop']         # ← get shop from view

        # Bill number unique PER SHOP
        last_invoice = Invoice.objects.filter(shop=shop).order_by('-bill_number').first()
        if last_invoice:
            validated_data['bill_number'] = last_invoice.bill_number + 1
        else:
            # First bill for this shop
            if shop.id == 1:
                validated_data['bill_number'] = 21228   # continues Shop 1's paper bills
            else:
                validated_data['bill_number'] = 1001    # Shop 2 starts fresh

        subtotal = sum(
            float(item['quantity']) * float(item['rate'])
            for item in items_data
        )
        subtotal = round(subtotal, 2)
        cgst     = round(subtotal * 0.09, 2)
        sgst     = round(subtotal * 0.09, 2)
        total    = round(subtotal + cgst + sgst, 2)

        validated_data['shop']         = shop
        validated_data['subtotal']     = subtotal
        validated_data['cgst_amount']  = cgst
        validated_data['sgst_amount']  = sgst
        validated_data['total_amount'] = total

        invoice = Invoice.objects.create(**validated_data)

        for i, item_data in enumerate(items_data, start=1):
            InvoiceItem.objects.create(
                invoice     = invoice,
                sl_no       = i,
                particulars = item_data['particulars'],
                quantity    = item_data['quantity'],
                rate        = item_data['rate'],
                amount      = round(
                    float(item_data['quantity']) * float(item_data['rate']), 2
                )
            )
        return invoice