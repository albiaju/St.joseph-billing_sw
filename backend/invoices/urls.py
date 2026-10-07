from django.urls import path
from .views import InvoiceListCreateView, InvoiceDetailView, InvoicePDFView

urlpatterns = [
    path('', InvoiceListCreateView.as_view()),
    path('<int:pk>/', InvoiceDetailView.as_view()),
    path('<int:pk>/pdf/', InvoicePDFView.as_view()),
]