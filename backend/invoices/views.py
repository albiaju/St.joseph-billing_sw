from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.http import HttpResponse
from .models import Invoice, InvoiceItem
from .serializers import InvoiceSerializer
from .pdf_generator import generate_invoice_pdf


class InvoiceListCreateView(APIView):

    def get(self, request):
        # Optional filters: ?month=4&year=2026
        invoices = Invoice.objects.all()

        month = request.query_params.get('month')
        year = request.query_params.get('year')

        if month and year:
            invoices = invoices.filter(date__month=month, date__year=year)
        elif year:
            invoices = invoices.filter(date__year=year)

        serializer = InvoiceSerializer(invoices, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = InvoiceSerializer(data=request.data)
        if serializer.is_valid():
            invoice = serializer.save()
            return Response(
                InvoiceSerializer(invoice).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InvoiceDetailView(APIView):

    def get_object(self, pk):
        try:
            return Invoice.objects.get(pk=pk)
        except Invoice.DoesNotExist:
            return None

    def get(self, request, pk):
        invoice = self.get_object(pk)
        if not invoice:
            return Response({'error': 'Invoice not found'}, status=404)
        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data)

    def delete(self, request, pk):
        # This cancels the bill (soft delete - keeps record but marks cancelled)
        invoice = self.get_object(pk)
        if not invoice:
            return Response({'error': 'Invoice not found'}, status=404)
        if invoice.is_cancelled:
            return Response({'error': 'Already cancelled'}, status=400)

        invoice.is_cancelled = True
        invoice.cancelled_at = timezone.now()
        invoice.save()
        return Response({'message': f'Bill #{invoice.bill_number} cancelled successfully'})


class InvoicePDFView(APIView):

    def get(self, request, pk):
        try:
            invoice = Invoice.objects.prefetch_related('items').get(pk=pk)
        except Invoice.DoesNotExist:
            return Response({'error': 'Invoice not found'}, status=404)

        pdf_buffer = generate_invoice_pdf(invoice)

        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="Invoice_{invoice.bill_number}.pdf"'
        )
        return response