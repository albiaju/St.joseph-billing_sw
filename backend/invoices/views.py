from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.http import HttpResponse
from .models import Invoice, InvoiceItem
from .serializers import InvoiceSerializer
from .pdf_generator import generate_invoice_pdf


def get_shop(request):
    """Helper — gets the shop for the logged-in user."""
    if not request.user.is_authenticated:
        return None
    try:
        return request.user.shop
    except:
        return None


class InvoiceListCreateView(APIView):

    def get(self, request):
        shop = get_shop(request)
        if not shop:
            return Response({'error': 'Not logged in'}, status=401)

        # ONLY fetch invoices for THIS shop
        invoices = Invoice.objects.filter(shop=shop)

        month = request.query_params.get('month')
        year  = request.query_params.get('year')
        if month and year:
            invoices = invoices.filter(date__month=month, date__year=year)

        serializer = InvoiceSerializer(invoices, many=True)
        return Response(serializer.data)

    def post(self, request):
        shop = get_shop(request)
        if not shop:
            return Response({'error': 'Not logged in'}, status=401)

        serializer = InvoiceSerializer(
            data=request.data,
            context={'shop': shop}      # pass shop into serializer
        )
        if serializer.is_valid():
            invoice = serializer.save()
            return Response(
                InvoiceSerializer(invoice).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=400)


class InvoiceDetailView(APIView):

    def get_object(self, pk, shop):
        try:
            # Can only access invoices belonging to THIS shop
            return Invoice.objects.get(pk=pk, shop=shop)
        except Invoice.DoesNotExist:
            return None

    def get(self, request, pk):
        shop = get_shop(request)
        if not shop:
            return Response({'error': 'Not logged in'}, status=401)
        invoice = self.get_object(pk, shop)
        if not invoice:
            return Response({'error': 'Invoice not found'}, status=404)
        return Response(InvoiceSerializer(invoice).data)

    def delete(self, request, pk):
        shop = get_shop(request)
        if not shop:
            return Response({'error': 'Not logged in'}, status=401)
        invoice = self.get_object(pk, shop)
        if not invoice:
            return Response({'error': 'Invoice not found'}, status=404)
        if invoice.is_cancelled:
            return Response({'error': 'Already cancelled'}, status=400)
        invoice.is_cancelled = True
        invoice.cancelled_at = timezone.now()
        invoice.save()
        return Response({'message': f'Bill #{invoice.bill_number} cancelled'})


class InvoicePDFView(APIView):

    def get(self, request, pk):
        shop = get_shop(request)
        if not shop:
            return Response({'error': 'Not logged in'}, status=401)
        try:
            invoice = Invoice.objects.prefetch_related('items').get(
                pk=pk, shop=shop
            )
        except Invoice.DoesNotExist:
            return Response({'error': 'Invoice not found'}, status=404)

        pdf_buffer = generate_invoice_pdf(invoice, shop)
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="Invoice_{invoice.bill_number}.pdf"'
        )
        return response