from django.urls import path
from .views import PaymentFormView, PaymentStatusView

app_name = 'payments'

urlpatterns = [
    path('payment/<int:order_id>/', PaymentFormView.as_view(), name='payment_form'),
    path('status/<int:order_id>/', PaymentStatusView.as_view(), name='payment_status'),
]